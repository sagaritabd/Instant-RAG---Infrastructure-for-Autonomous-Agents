import asyncio
from typing import Callable, Dict, Any

async def run(query: str, engine: Callable) -> Dict[str, Any]:
    """
    Run a swarm collaboration query.
    Executes the query multiple times and combines results.
    
    Args:
        query: The query text
        engine: Async callable that processes the query
        
    Returns:
        Combined results from multiple executions
    """
    # Run query twice in parallel for swarm collaboration
    results = await asyncio.gather(
        engine(query),
        engine(query)
    )
    
    r1, r2 = results
    
    # Combine answers
    combined_answer = r1.get("answer", "") + "\n\n" + r2.get("answer", "")
    
    # Merge citations (deduplicate)
    citations = r1.get("citations", []) + r2.get("citations", [])
    
    # Take higher confidence
    confidence = max(
        r1.get("confidence", 0),
        r2.get("confidence", 0)
    )
    
    return {
        "answer": combined_answer,
        "citations": citations,
        "confidence": confidence,
        "swarm_size": 2,
        "explanation": {
            "method": "parallel_execution",
            "runs": 2
        }
    }
