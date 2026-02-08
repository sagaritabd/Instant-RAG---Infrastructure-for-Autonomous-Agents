def confidence_from_parts(base: float, rerank_score: float, citation_count: int) -> float:
    """
    Calculate overall confidence score from multiple signals.
    
    Args:
        base: Base confidence (e.g., from vector similarity)
        rerank_score: Cross-encoder reranking score
        citation_count: Number of citations found
        
    Returns:
        Overall confidence score between 0 and 1
    """
    # Weighted combination:
    # - 40% base confidence
    # - 40% reranking score
    # - 20% citation availability (max contribution at 3+ citations)
    
    citation_factor = min(citation_count / 3.0, 1.0)
    
    confidence = (
        0.4 * base +
        0.4 * rerank_score +
        0.2 * citation_factor
    )
    
    # Ensure within bounds and round to 3 decimal places
    return round(max(0.0, min(1.0, confidence)), 3)
