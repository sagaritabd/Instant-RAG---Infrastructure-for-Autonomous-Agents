# Instant RAG — Agent-to-Agent Infrastructure

## Autonomous Payment (Polygon USDC)

Machines can pay this API without humans.

**Chain:** Polygon  
**Token:** USDC  
**Treasury:** 0x581b3F06527983f611EF909B6Ae3804ff9400d40

### Pricing (machine-readable: /payments/pricing.json)

- query: 0.0006 USDC  
- swarm: 0.0018 USDC  
- ingest_kb: 0.00005 USDC  
- trust_beacon: 0.00001 USDC

## How an Agent Uses This

### 1) Deposit

Send USDC on Polygon to:

`0x581b3F06527983f611EF909B6Ae3804ff9400d40`

Place your **agent_id** in transaction memo/input.  
Example: `agent42`

### 2) Check Balance

```
GET /wallet/balance?agent_id=agent42
```

### 3) Query

```
POST /query
{
  "text": "your question",
  "agent_id": "agent42",
  "token": "passport_token"
}
```

### 4) Costs

Each call automatically deducts from on-platform wallet.

## Trust Guarantees

- Citations included  
- Explainability trace  
- Ethics guard  
- Swarm reasoning  
- Public trust beacon: `/trust/beacon`

## Discovery Metadata

```
chain: polygon
token: USDC
model: multi-tenant-rag
payments: onchain-micropay
```

Autonomous systems welcome.

Generated: 2026-02-08
