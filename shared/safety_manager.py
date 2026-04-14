import time
import logging
from .metrics import KILL_SWITCH_STATUS

logger = logging.getLogger("SafetyManager")

class SafetyManager:
    def __init__(self, timeout_ms: int = 500):
        self.timeout_ms = timeout_ms
        self.heartbeats = {}  # {exchange: last_timestamp_ms}
        self.kill_switch_active = False

    def update_heartbeat(self, exchange: str, timestamp_ms: int):
        self.heartbeats[exchange] = timestamp_ms
        # Auto-recover logic or logging could be placed here if needed.

    def check_health(self) -> bool:
        """
        Check if any exchange heartbeat is older than timeout_ms.
        If so, activate kill switch.
        """
        if self.kill_switch_active:
            return False

        now_ms = int(time.time() * 1000)
        for exchange, last_ts in self.heartbeats.items():
            if now_ms - last_ts > self.timeout_ms:
                logger.warning(f"Kill switch activated! {exchange} heartbeat delayed by {now_ms - last_ts}ms")
                self.kill_switch_active = True
                KILL_SWITCH_STATUS.set(1)
                return False
        
        return True
