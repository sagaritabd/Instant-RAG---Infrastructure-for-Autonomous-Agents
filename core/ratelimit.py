import time
import collections
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class Limit:
    """
    Sliding window rate limiter.
    Tracks API calls per agent and enforces daily limits.
    """
    
    def __init__(self, per_day: int = 2000):
        self.calls: Dict[str, List[float]] = collections.defaultdict(list)
        self.per_day = per_day
        self.window_seconds = 86400  # 24 hours
    
    def allow(self, agent: str) -> bool:
        """
        Check if an agent is allowed to make a request.
        
        Args:
            agent: Agent identifier
            
        Returns:
            True if request is allowed, False if rate limited
        """
        try:
            now = time.time()
            
            # Clean up old entries outside the time window
            self.calls[agent] = [
                t for t in self.calls[agent] 
                if now - t < self.window_seconds
            ]
            
            # Check if limit exceeded
            if len(self.calls[agent]) >= self.per_day:
                logger.warning(f"Rate limit exceeded for agent: {agent}")
                return False
            
            # Record this call
            self.calls[agent].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error in rate limiter: {e}")
            # Fail open - allow the request if there's an error
            return True
    
    def get_usage(self, agent: str) -> Dict[str, int]:
        """
        Get current usage statistics for an agent.
        
        Args:
            agent: Agent identifier
            
        Returns:
            Dictionary with usage stats
        """
        now = time.time()
        self.calls[agent] = [
            t for t in self.calls[agent] 
            if now - t < self.window_seconds
        ]
        
        return {
            "used": len(self.calls[agent]),
            "limit": self.per_day,
            "remaining": self.per_day - len(self.calls[agent])
        }

limiter = Limit()
