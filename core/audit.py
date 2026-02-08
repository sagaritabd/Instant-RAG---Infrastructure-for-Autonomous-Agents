import json
import time
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

# Ensure data directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class Auditor:
    """
    Audit logging system for tracking all system events.
    """
    
    def record(self, event: str, agent: str, payload: Dict[str, Any]):
        """
        Record an audit event.
        
        Args:
            event: Event type (e.g., 'query', 'ingest')
            agent: Agent identifier
            payload: Event-specific data
        """
        try:
            entry = {
                "timestamp": time.time(),
                "event": event,
                "agent": agent,
                "payload": payload
            }
            
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
                
            logger.debug(f"Audit recorded: {event} for {agent}")
            
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            # Don't raise - audit logging shouldn't break the app
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all audit logs.
        
        Returns:
            List of audit log entries
        """
        try:
            if not os.path.exists(LOG_FILE):
                return []
            
            with open(LOG_FILE, "r") as f:
                return [json.loads(line) for line in f if line.strip()]
                
        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}")
            return []
    
    def read_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """
        Read audit logs for a specific agent.
        
        Args:
            agent: Agent identifier
            
        Returns:
            List of audit log entries for the agent
        """
        all_logs = self.read_all()
        return [log for log in all_logs if log.get("agent") == agent]
    
    def read_by_event(self, event: str) -> List[Dict[str, Any]]:
        """
        Read audit logs for a specific event type.
        
        Args:
            event: Event type
            
        Returns:
            List of audit log entries for the event
        """
        all_logs = self.read_all()
        return [log for log in all_logs if log.get("event") == event]

auditor = Auditor()
