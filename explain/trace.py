from typing import List, Dict, Any

def build_trace(q: str, cands: List[str], scores: List[float]) -> Dict[str, Any]:
    """
    Build an explanation trace for a query.
    
    Args:
        q: Query text
        cands: Candidate documents
        scores: Reranker scores
        
    Returns:
        Trace dictionary with query and steps
    """
    steps = []
    
    for i, (chunk, score) in enumerate(zip(cands, scores)):
        steps.append({
            "rank": i + 1,
            "chunk": chunk[:100] + "..." if len(chunk) > 100 else chunk,
            "score": float(score),
            "relevance": "high" if score > 0.5 else "medium" if score > 0.2 else "low"
        })
    
    return {
        "query": q,
        "method": "semantic_search_with_reranking",
        "steps": steps,
        "total_results": len(steps)
    }
