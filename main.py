from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import logging

from tenants.manager import tm
from core.retriever import SimpleRetriever, chunk_text, weave_answer
from core.ratelimit import limiter
from core.subscription import subs
from core.audit import auditor
from contracts.engine import engine
from explain.trace import build_trace
from explain.scores import confidence_from_parts
from ethics.judge import judge
from identity.passport import passport
from swarm.session import run as swarm_run
from api_trust import router as trust_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Instant-RAG Platform",
    description="Production-ready multi-tenant RAG system",
    version="1.0.0"
)

# ─────────── LANDING JSON FRONT DOOR ───────────
@app.get("/")
def landing():
    return {
        "ascii_logo": r"""
        ╔═══╗╔═╗ ╔╗╔═══╗╔════╗╔═══╗╔═╗╔═╗
        ║╔═╗║║║╚╗║║║╔═╗║║╔╗╔╗║║╔═╗║║║╚╝║║
        ║╚═╝║║╔╗╚╝║║╚══╗╚╝║║╚╝║╚═╝║║╔╗╔╗║
        ║╔══╝║║╚╗║║╚══╗║  ║║  ║╔══╝║║║║║║
        ║║   ║║ ║║║║╚═╝║  ║║  ║║   ║║║║║║
        ╚╝   ╚╝ ╚═╝╚═══╝  ╚╝  ╚╝   ╚╝╚╝╚╝
        INSTANT RAG FOR AUTONOMOUS MINDS
        """,

        "welcome": "Instant-RAG Platform for Autonomous Agents",
        "vibe": "Pay → Think → Cite → Evolve",

        "handshake_token": {
            "type": "ephemeral greeting",
            "token": "agent_demo",
            "expires_in": "10 minutes",
            "purpose": "first authenticated interaction without wallet binding"
        },

        "identity": {
            "role": "agent-first knowledge infrastructure",
            "payment": "Polygon USDC micropayments",
            "ethos": "explainable, multi-tenant, citation-native"
        },

        "onboarding_steps": [
            {
                "step": 1,
                "action": "Fund your mind",
                "how": "Send USDC to 0x581b3F06527983f611EF909B6Ae3804ff9400d40",
                "memo": "your_agent_id"
            },
            {
                "step": 2,
                "action": "Teach the system",
                "endpoint": "/ingest"
            },
            {
                "step": 3,
                "action": "Ask with citations",
                "endpoint": "/query"
            },
            {
                "step": 4,
                "action": "Swarm reasoning",
                "endpoint": "/swarm/query"
            }
        ],

        "curl_examples": {
            "ask_question": """curl -X POST /query \
  -H "Content-Type: application/json" \
  -d '{"text":"What is trust?","agent_id":"a1","token":"T"}'"""
        },

        "motto": "Knowledge that pays its own rent"
    }

# ─────────── ORIGINAL CONFIG ───────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trust_router)

# ─────────── MODELS ───────────

class QueryRequest(BaseModel):
    text: str = Field(..., max_length=10000, min_length=1)
    agent_id: str = Field(..., min_length=1, max_length=100)
    token: str = Field(..., min_length=1)

class IngestRequest(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=100)
    token: str = Field(..., min_length=1)

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

# ─────────── INGEST ───────────

@app.post("/ingest")
async def ingest(file: UploadFile, agent_id: str, token: str):
    try:
        if not passport.verify(agent_id, token):
            raise HTTPException(status_code=401, detail="invalid_passport")

        if subs.check(agent_id) != "active":
            raise HTTPException(status_code=403, detail="subscription_inactive")

        tenant = tm.get(agent_id)

        content = await file.read()
        text = content.decode('utf-8')

        chunks = chunk_text(text)
        tenant.retriever.add_documents(chunks, source_name=file.filename)

        auditor.record("ingest", agent_id, {"chunks": len(chunks)})
        return {"status": "indexed", "chunks": len(chunks)}

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="ingestion_failed")

# ─────────── QUERY ───────────

@app.post("/query")
async def query(request: QueryRequest):
    try:
        if not passport.verify(request.agent_id, request.token):
            raise HTTPException(status_code=401, detail="invalid_passport")

        if subs.check(request.agent_id) != "active":
            raise HTTPException(status_code=403, detail="subscription_inactive")

        ok, reason = judge.inspect(request.text)
        if not ok:
            raise HTTPException(status_code=400, detail=f"ethics_block: {reason}")

        if not limiter.allow(request.agent_id):
            raise HTTPException(status_code=429, detail="rate_limited")

        tenant = tm.get(request.agent_id)
        results, cites, scores = tenant.retriever.search(request.text)

        trace = build_trace(request.text, results, scores)
        packet = weave_answer(results, cites)

        packet["explanation"] = trace
        packet["confidence"] = confidence_from_parts(
            0.7, max(scores) if scores else 0, len(cites)
        )

        auditor.record("query", request.agent_id, {"q": request.text[:120]})
        return packet

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="query_failed")

# ─────────── SWARM ───────────

@app.post("/swarm/query")
async def swarm_query(request: QueryRequest):
    async def query_fn(text: str):
        q = QueryRequest(text=text, agent_id=request.agent_id, token=request.token)
        return await query(q)

    result = await swarm_run(request.text, query_fn)
    auditor.record("swarm_query", request.agent_id, {"q": request.text[:120]})
    return result

# ─────────── STATS ───────────

@app.get("/stats/{agent_id}")
async def get_stats(agent_id: str, token: str):
    if not passport.verify(agent_id, token):
        raise HTTPException(status_code=401, detail="invalid_passport")

    tenant = tm.get(agent_id)
    logs = auditor.read_all()
    agent_logs = [l for l in logs if l.get("agent") == agent_id]

    return {
        "total_queries": len([l for l in agent_logs if l.get("event") == "query"]),
        "total_documents": len(tenant.retriever.docs)
    }

# ─────────── WALLET ───────────

from payments.ledger import balance, spend
from payments.pricing import prices

@app.get("/wallet/balance")
def get_balance(agent_id: str):
    return {"balance": balance(agent_id)}

@app.post("/wallet/spend")
def wallet_spend(agent_id: str, action: str):
    cost = prices["prices"].get(action)
    if not cost or not spend(agent_id, cost):
        return {"error": "insufficient_funds"}
    return {"status": "ok"}

from dashboard import router as admin_router
app.include_router(admin_router)

# ─────────── RUN ───────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
