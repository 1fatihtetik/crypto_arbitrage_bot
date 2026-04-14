import asyncio
import logging
import json
import time
import random
from shared.safety_manager import SafetyManager
from strategies.spatial_arbitrage import SpatialArbitrageEngine
from executors.executor import MockExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TestDynamic")

class MockRedisManager:
    """A simplified in-memory pub/sub mimicking redis streams for testing"""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.current_id = 1

    async def publish_orderbook(self, update_data: dict):
        message_id = f"{self.current_id}-0"
        self.current_id += 1
        msg = {"data": json.dumps(update_data)}
        await self.queue.put((message_id, msg))

    async def get_stream_iterator(self, last_id="$", block=0, count=100):
        msgs = []
        if self.queue.empty() and block > 0:
            try:
                # wait for block ms
                msg = await asyncio.wait_for(self.queue.get(), timeout=block/1000.0)
                msgs.append(msg)
            except asyncio.TimeoutError:
                pass
        
        while not self.queue.empty() and len(msgs) < count:
            msgs.append(self.queue.get_nowait())

        if msgs:
            return [("orderbook_stream", msgs)]
        return []

class MockDataIngestor:
    def __init__(self, redis_manager, exchanges):
        self.redis_manager = redis_manager
        self.exchanges = exchanges
        
    async def stream_orderbook(self, exchange_name: str, delay_seconds=0.1):
        base_price = 50000.0
        while True:
            # Simulate real market random walk
            base_price += random.uniform(-10, 10)
            
            bid_price = base_price - 1.0
            ask_price = base_price + 1.0
            
            # Artificial arbitrage scenario! Overprice binance randomly
            if exchange_name == "binance" and random.random() > 0.85:
                # Create a big synthetic drop which makes selling elsewhere profitable
                ask_price -= 100 
                bid_price -= 100

            # Ingest lag scenario to trigger KILL SWITCH!
            if exchange_name == "okx" and random.random() > 0.95:
                # Sleep heavily to trigger >500ms safety manager timeout
                logger.warning(f"Simulating large network lag for {exchange_name}...")
                await asyncio.sleep(0.8)
                
            update_data = {
                "exchange": exchange_name,
                "symbol": "BTC/USD",
                "bids": [[bid_price, 1.0]],
                "asks": [[ask_price, 1.0]],
                "timestamp": int(time.time() * 1000)
            }
            await self.redis_manager.publish_orderbook(update_data)
            await asyncio.sleep(delay_seconds)
            
    async def run_all(self):
        tasks = [self.stream_orderbook(ex_name) for ex_name in self.exchanges]
        await asyncio.gather(*tasks)

async def run_test():
    logger.info("Starting Dynamic Bot Skills Demonstration...")
    
    redis_manager = MockRedisManager()
    # 500ms kill switch
    safety_manager = SafetyManager(timeout_ms=500) 
    
    exchanges = ["binance", "kraken", "okx"]
    ingestor = MockDataIngestor(redis_manager, exchanges)
    strategy_engine = SpatialArbitrageEngine(redis_manager, safety_manager)
    # Give strategy engine the safety manager to check health and update heartbeats
    executor = MockExecutor(safety_manager) 
    
    # Run tasks concurrently
    task1 = asyncio.create_task(ingestor.run_all())
    task2 = asyncio.create_task(strategy_engine.run())
    
    # Stop after 10 seconds of simulation
    await asyncio.sleep(10)
    task1.cancel()
    task2.cancel()
    logger.info("Dynamic test completed.")

if __name__ == "__main__":
    asyncio.run(run_test())
