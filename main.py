import asyncio
import logging
from shared.config import METRICS_PORT, KILL_SWITCH_TIMEOUT_MS
from shared.metrics import start_metrics_server
from shared.redis_client import RedisManager
from shared.safety_manager import SafetyManager
from ingestors.ccxt_ingestor import DataIngestor
from strategies.spatial_arbitrage import SpatialArbitrageEngine
from executors.executor import MockExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Main")

async def main():
    logger.info("Initializing Cryptocurrency Arbitrage Bot Workspace...")
    
    # 1. Start Metrics Server
    start_metrics_server(METRICS_PORT)
    logger.info(f"Prometheus metrics server started on port {METRICS_PORT}")
    
    # 2. Initialize Shared Components
    redis_manager = RedisManager()
    safety_manager = SafetyManager(timeout_ms=KILL_SWITCH_TIMEOUT_MS)
    
    # 3. Initialize Modules
    ingestor = DataIngestor(redis_manager)
    strategy_engine = SpatialArbitrageEngine(redis_manager, safety_manager)
    executor = MockExecutor(safety_manager) # Setup and ready
    
    # 4. Run Concurrent Tasks
    logger.info("Starting ingestor and strategy engine streams...")
    await asyncio.gather(
        ingestor.run_all(),
        strategy_engine.run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully.")
