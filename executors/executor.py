import logging
from shared.safety_manager import SafetyManager

logger = logging.getLogger("MockExecutor")

class MockExecutor:
    def __init__(self, safety_manager: SafetyManager):
        self.safety_manager = safety_manager

    def execute_arbitrage(self, buy_exchange: str, sell_exchange: str, size: float):
        if not self.safety_manager.check_health():
            logger.warning("Execution blocked by Safety Manager: Kill Switch Active")
            return False
            
        logger.info(f"MOCK EXECUTION: Buying {size} on {buy_exchange}, Selling {size} on {sell_exchange}")
        return True
