from typing import Tuple, Dict

def compute() -> Tuple[float, Dict[str, float]]:
    """
    Compute trust beacon score and signal breakdown.
    
    The trust beacon provides transparency metrics across multiple dimensions:
    - Citations: How well sources are attributed
    - Privacy: Data protection measures
    - Pricing: Pricing transparency
    - Carbon: Environmental impact
    
    Returns:
        Tuple of (overall_score, signal_breakdown)
    """
    # Individual trust signals (0-1 scale)
    signals = {
        "citations": 0.9,      # Strong citation practices
        "privacy": 0.9,        # Good privacy protections
        "pricing": 0.8,        # Clear pricing
        "carbon": 0.7,         # Carbon footprint tracking
        "security": 0.85,      # Security measures
        "transparency": 0.88   # Overall transparency
    }
    
    # Calculate weighted overall score
    weights = {
        "citations": 0.2,
        "privacy": 0.25,
        "pricing": 0.15,
        "carbon": 0.1,
        "security": 0.2,
        "transparency": 0.1
    }
    
    overall_score = sum(
        signals[key] * weights[key]
        for key in signals.keys()
    )
    
    # Round to 2 decimal places
    overall_score = round(overall_score, 2)
    
    return overall_score, signals
