from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SubscriptionStatus(str, Enum):
    """Subscription status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"

class SubscriptionPlan(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Subs:
    """
    Subscription management system.
    Tracks agent subscription status and plans.
    """
    
    def __init__(self):
        self.records: Dict[str, Dict[str, Any]] = {}
        self._init_default_subscriptions()
    
    def _init_default_subscriptions(self):
        """Initialize with default active subscriptions for testing"""
        # You can remove this in production
        pass
    
    def check(self, agent: str) -> str:
        """
        Check subscription status for an agent.
        
        Args:
            agent: Agent identifier
            
        Returns:
            Subscription status (active, inactive, suspended, trial)
        """
        record = self.records.get(agent, {})
        status = record.get("status", SubscriptionStatus.ACTIVE)
        
        logger.debug(f"Subscription check for {agent}: {status}")
        return status
    
    def activate(self, agent: str, plan: str = SubscriptionPlan.FREE):
        """
        Activate a subscription for an agent.
        
        Args:
            agent: Agent identifier
            plan: Subscription plan
        """
        self.records[agent] = {
            "status": SubscriptionStatus.ACTIVE,
            "plan": plan,
            "activated_at": None  # Add timestamp in production
        }
        logger.info(f"Activated {plan} subscription for {agent}")
    
    def suspend(self, agent: str):
        """
        Suspend a subscription.
        
        Args:
            agent: Agent identifier
        """
        if agent in self.records:
            self.records[agent]["status"] = SubscriptionStatus.SUSPENDED
            logger.warning(f"Suspended subscription for {agent}")
    
    def get_plan(self, agent: str) -> str:
        """
        Get the subscription plan for an agent.
        
        Args:
            agent: Agent identifier
            
        Returns:
            Subscription plan name
        """
        record = self.records.get(agent, {})
        return record.get("plan", SubscriptionPlan.FREE)
    
    def get_limits(self, agent: str) -> Dict[str, int]:
        """
        Get usage limits based on subscription plan.
        
        Args:
            agent: Agent identifier
            
        Returns:
            Dictionary of limits
        """
        plan = self.get_plan(agent)
        
        limits = {
            SubscriptionPlan.FREE: {
                "queries_per_day": 100,
                "documents": 10,
                "max_file_size": 1024 * 1024  # 1MB
            },
            SubscriptionPlan.BASIC: {
                "queries_per_day": 1000,
                "documents": 100,
                "max_file_size": 10 * 1024 * 1024  # 10MB
            },
            SubscriptionPlan.PRO: {
                "queries_per_day": 5000,
                "documents": 1000,
                "max_file_size": 50 * 1024 * 1024  # 50MB
            },
            SubscriptionPlan.ENTERPRISE: {
                "queries_per_day": -1,  # Unlimited
                "documents": -1,  # Unlimited
                "max_file_size": 100 * 1024 * 1024  # 100MB
            }
        }
        
        return limits.get(plan, limits[SubscriptionPlan.FREE])

subs = Subs()
