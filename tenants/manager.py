from core.retriever import SimpleRetriever
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class Tenant:
    """
    Represents a single tenant (agent) with isolated resources.
    """
    
    def __init__(self, id: str):
        self.id = id
        self.retriever = SimpleRetriever()
        logger.info(f"Created tenant: {id}")
    
    def __repr__(self):
        return f"Tenant(id={self.id}, docs={len(self.retriever.docs)})"

class Manager:
    """
    Multi-tenant manager.
    Handles tenant lifecycle and isolation.
    """
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
    
    def get(self, id: str) -> Tenant:
        """
        Get or create a tenant.
        
        Args:
            id: Tenant identifier
            
        Returns:
            Tenant instance
        """
        if id not in self.tenants:
            self.tenants[id] = Tenant(id)
            logger.info(f"Created new tenant: {id}")
        
        return self.tenants[id]
    
    def exists(self, id: str) -> bool:
        """
        Check if a tenant exists.
        
        Args:
            id: Tenant identifier
            
        Returns:
            True if tenant exists
        """
        return id in self.tenants
    
    def delete(self, id: str) -> bool:
        """
        Delete a tenant and all associated data.
        
        Args:
            id: Tenant identifier
            
        Returns:
            True if tenant was deleted
        """
        if id in self.tenants:
            del self.tenants[id]
            logger.warning(f"Deleted tenant: {id}")
            return True
        return False
    
    def list_tenants(self):
        """
        List all active tenants.
        
        Returns:
            List of tenant IDs
        """
        return list(self.tenants.keys())
    
    def get_stats(self):
        """
        Get statistics about all tenants.
        
        Returns:
            Dictionary with tenant statistics
        """
        return {
            "total_tenants": len(self.tenants),
            "tenants": [
                {
                    "id": tid,
                    "documents": len(tenant.retriever.docs)
                }
                for tid, tenant in self.tenants.items()
            ]
        }

tm = Manager()
