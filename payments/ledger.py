import json, os, time, threading

DB = "data/wallet.json"
LOCK = threading.Lock()

def _load():
    if not os.path.exists(DB):
        return {"agents": {}, "txs": []}
    return json.load(open(DB))

def _save(d):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    json.dump(d, open(DB, "w"), indent=2)

def credit(agent, amount, tx):
    with LOCK:
        d = _load()
        a = d["agents"].setdefault(agent, {"balance": 0})
        a["balance"] += amount
        d["txs"].append({
            "agent": agent,
            "tx": tx,
            "amount": amount,
            "time": time.time()
        })
        _save(d)

def spend(agent, amount):
    with LOCK:
        d = _load()
        if d["agents"].get(agent, {}).get("balance", 0) < amount:
            return False
        d["agents"][agent]["balance"] -= amount
        _save(d)
        return True

def balance(agent):
    return _load()["agents"].get(agent, {}).get("balance", 0)
