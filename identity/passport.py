import hashlib
import time
import json
import os
import secrets
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

IDENTITY_DIR = "identity"
REG_FILE = os.path.join(IDENTITY_DIR, "registry.json")

# Ensure identity directory exists
os.makedirs(IDENTITY_DIR, exist_ok=True)

# Initialize registry file if it doesn't exist
if not os.path.exists(REG_FILE):
    with open(REG_FILE, "w") as f:
        json.dump({"agents": {}}, f)

class Passport:
    """
    Identity and authentication system.
    Manages agent registration and token verification.
    """
    
    def _load(self) -> Dict[str, Any]:
        """Load the registry from disk"""
        try:
            with open(REG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"agents": {}}
    
    def _save(self, data: Dict[str, Any]):
        """Save the registry to disk"""
        try:
            with open(REG_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def issue(self, agent: str, role: str = "agent") -> str:
        """
        Issue a new passport token for an agent.
        
        Args:
            agent: Agent identifier
            role: Agent role (agent, admin, etc.)
            
        Returns:
            Authentication token
        """
        try:
            data = self._load()
            
            # Generate secure token
            random_salt = secrets.token_hex(16)
            token_input = f"{agent}:{time.time()}:{random_salt}"
            token = hashlib.sha256(token_input.encode()).hexdigest()
            
            # Store agent record
            data["agents"][agent] = {
                "token": token,
                "role": role,
                "issued_at": time.time()
            }
            
            self._save(data)
            logger.info(f"Issued passport for agent: {agent}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to issue passport: {e}")
            raise
    
    def verify(self, agent: str, token: str) -> bool:
        """
        Verify an agent's authentication token.
        
        Args:
            agent: Agent identifier
            token: Token to verify
            
        Returns:
            True if token is valid
        """
        try:
            data = self._load()
            record = data["agents"].get(agent)
            
            if not record:
                logger.warning(f"No record found for agent: {agent}")
                return False
            
            is_valid = record["token"] == token
            
            if not is_valid:
                logger.warning(f"Invalid token for agent: {agent}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return False
    
    def revoke(self, agent: str) -> bool:
        """
        Revoke an agent's passport.
        
        Args:
            agent: Agent identifier
            
        Returns:
            True if passport was revoked
        """
        try:
            data = self._load()
            
            if agent in data["agents"]:
                del data["agents"][agent]
                self._save(data)
                logger.warning(f"Revoked passport for agent: {agent}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke passport: {e}")
            return False
    
    def get_role(self, agent: str) -> Optional[str]:
        """
        Get the role of an agent.
        
        Args:
            agent: Agent identifier
            
        Returns:
            Agent role or None
        """
        try:
            data = self._load()
            record = data["agents"].get(agent)
            return record.get("role") if record else None
        except Exception as e:
            logger.error(f"Failed to get role: {e}")
            return None
    
    def list_agents(self):
        """
        List all registered agents.
        
        Returns:
            List of agent identifiers
        """
        try:
            data = self._load()
            return list(data["agents"].keys())
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []

passport = Passport()
