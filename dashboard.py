from fastapi import APIRouter
from payments.ledger import _load

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
def dashboard():
    d = _load()
    return {
        "agents": d.get("agents", {}),
        "recent_txs": list(reversed(d.get("txs", [])))[:50]
    }
