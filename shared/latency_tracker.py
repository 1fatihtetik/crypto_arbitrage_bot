import time
import logging
from typing import Dict

logger = logging.getLogger("LatencyTracker")

class LatencyTracker:
    def __init__(self, rtt_threshold_ms: float = 10.0):
        """
        :param rtt_threshold_ms: Maximum acceptable round-trip time in milliseconds.
        """
        self.rtt_threshold_ms = rtt_threshold_ms
        self.ping_starts: Dict[str, float] = {}
        self.current_rtt: Dict[str, float] = {}

    def start_ping(self, exchange: str):
        """Record the start time of a network request."""
        self.ping_starts[exchange] = time.perf_counter()

    def record_pong(self, exchange: str):
        """Record the end time and calculate RTT."""
        start_time = self.ping_starts.get(exchange)
        if start_time is None:
            return
        
        rtt_ms = (time.perf_counter() - start_time) * 1000
        self.current_rtt[exchange] = rtt_ms
        del self.ping_starts[exchange]
        
        # In a real system, you might emit a metric to Prometheus here
        if rtt_ms > self.rtt_threshold_ms:
            logger.warning(f"High Latency detected on {exchange}: {rtt_ms:.2f}ms (Threshold: {self.rtt_threshold_ms}ms)")

    def is_latency_acceptable(self, exchange: str) -> bool:
        """Check if current latency is within safe bounds to trade."""
        rtt = self.current_rtt.get(exchange, 0.0)
        return rtt <= self.rtt_threshold_ms

    def get_latency(self, exchange: str) -> float:
        return self.current_rtt.get(exchange, 0.0)
