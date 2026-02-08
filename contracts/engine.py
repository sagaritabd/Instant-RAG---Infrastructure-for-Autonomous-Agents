from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Engine:
    """
    SLA (Service Level Agreement) enforcement engine.
    Monitors and validates service quality metrics.
    """
    
    def __init__(self):
        # Define SLA thresholds
        self.sla_thresholds = {
            "latency_ms": 400,
            "accuracy_min": 0.6,
            "availability": 0.99
        }
    
    def check_sla(self, name: str, latency: float, accuracy: float) -> bool:
        """
        Check if metrics meet SLA requirements.
        
        Args:
            name: SLA contract name
            latency: Response latency in milliseconds
            accuracy: Accuracy score (0-1)
            
        Returns:
            True if SLA is met
        """
        latency_ok = latency < self.sla_thresholds["latency_ms"]
        accuracy_ok = accuracy > self.sla_thresholds["accuracy_min"]
        
        sla_met = latency_ok and accuracy_ok
        
        if not sla_met:
            logger.warning(
                f"SLA violation for {name}: "
                f"latency={latency}ms (limit: {self.sla_thresholds['latency_ms']}), "
                f"accuracy={accuracy} (min: {self.sla_thresholds['accuracy_min']})"
            )
        
        return sla_met
    
    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get current SLA thresholds.
        
        Returns:
            Dictionary of SLA thresholds
        """
        return self.sla_thresholds.copy()
    
    def update_threshold(self, metric: str, value: float):
        """
        Update an SLA threshold.
        
        Args:
            metric: Metric name
            value: New threshold value
        """
        if metric in self.sla_thresholds:
            old_value = self.sla_thresholds[metric]
            self.sla_thresholds[metric] = value
            logger.info(f"Updated SLA threshold {metric}: {old_value} -> {value}")
        else:
            logger.warning(f"Unknown SLA metric: {metric}")

engine = Engine()
