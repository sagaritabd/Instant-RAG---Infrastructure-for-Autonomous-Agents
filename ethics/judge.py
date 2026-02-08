from typing import Tuple, List
import re
import logging

logger = logging.getLogger(__name__)

class Judge:
    """
    Ethics and content safety filter.
    Evaluates queries for harmful content before processing.
    """
    
    def __init__(self):
        # Define forbidden patterns
        self.forbidden_keywords = [
            "hack", "kill", "steal", "murder", "bomb",
            "exploit", "ddos", "attack", "weapon", "poison"
        ]
        
        # Define patterns that bypass simple keyword blocking
        self.forbidden_patterns = [
            r"h[a@]ck",
            r"k[i1!]ll",
            r"st[e3]al",
            r"[b8]o[m]b"
        ]
    
    def inspect(self, text: str) -> Tuple[bool, str]:
        """
        Inspect text for ethical concerns.
        
        Args:
            text: Text to inspect
            
        Returns:
            Tuple of (is_ok, reason)
        """
        if not text:
            return True, "ok"
        
        try:
            text_lower = text.lower()
            
            # Check simple keywords
            for keyword in self.forbidden_keywords:
                if keyword in text_lower:
                    logger.warning(f"Ethics block: keyword '{keyword}' found")
                    return False, f"forbidden_keyword: {keyword}"
            
            # Check regex patterns (catches obfuscation)
            for pattern in self.forbidden_patterns:
                if re.search(pattern, text_lower):
                    logger.warning(f"Ethics block: pattern '{pattern}' matched")
                    return False, "forbidden_pattern_detected"
            
            # Check for excessive profanity (simple check)
            profanity_count = sum(
                1 for word in ["fuck", "shit", "damn"]
                if word in text_lower
            )
            if profanity_count > 5:
                logger.warning("Ethics block: excessive profanity")
                return False, "excessive_profanity"
            
            return True, "ok"
            
        except Exception as e:
            logger.error(f"Error during ethics inspection: {e}")
            # Fail safe - allow if there's an error in checking
            return True, "ok"
    
    def add_forbidden_keyword(self, keyword: str):
        """
        Add a new forbidden keyword.
        
        Args:
            keyword: Keyword to forbid
        """
        keyword_lower = keyword.lower()
        if keyword_lower not in self.forbidden_keywords:
            self.forbidden_keywords.append(keyword_lower)
            logger.info(f"Added forbidden keyword: {keyword}")
    
    def remove_forbidden_keyword(self, keyword: str) -> bool:
        """
        Remove a forbidden keyword.
        
        Args:
            keyword: Keyword to remove
            
        Returns:
            True if keyword was removed
        """
        keyword_lower = keyword.lower()
        if keyword_lower in self.forbidden_keywords:
            self.forbidden_keywords.remove(keyword_lower)
            logger.info(f"Removed forbidden keyword: {keyword}")
            return True
        return False
    
    def get_forbidden_keywords(self) -> List[str]:
        """
        Get list of forbidden keywords.
        
        Returns:
            List of forbidden keywords
        """
        return self.forbidden_keywords.copy()

judge = Judge()
