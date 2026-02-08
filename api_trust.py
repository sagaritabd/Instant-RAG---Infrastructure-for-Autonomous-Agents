from fastapi import APIRouter
from trust.beacon import compute

router = APIRouter(prefix="/trust", tags=["trust"])

@router.get("/beacon")
def get_trust_beacon():
    """
    Get trust beacon score and transparency signals.
    
    Returns trust metrics across multiple dimensions:
    - Overall trust score
    - Individual signal scores (citations, privacy, pricing, carbon, etc.)
    """
    score, signals = compute()
    
    return {
        "score": score,
        "signals": signals,
        "description": "Trust beacon provides transparency across key dimensions"
    }
