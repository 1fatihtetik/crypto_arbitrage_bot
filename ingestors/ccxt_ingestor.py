import asyncio
import ccxt.pro as ccxt  # Using ccxt.pro for websocket support
import time
import logging
from typing import Dict
from shared.config import SYMBOL, EXCHANGES
from shared.redis_client import RedisManager
from shared.metrics import INGESTOR_LATENCY

logger = logging.getLogger("CCXTIngestor")

class DataIngestor:
    def __init__(self, redis_manager: RedisManager):
        self.redis_manager = redis_manager
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        for ex_name in EXCHANGES:
            # instantiate ccxt pro exchange class
            exchange_class = getattr(ccxt, ex_name)
            self.exchanges[ex_name] = exchange_class({'enableRateLimit': True})

    async def stream_orderbook(self, exchange_name: str):
        exchange = self.exchanges[exchange_name]
        try:
            while True:
                start_time = time.time()
                # watch_order_book streams L2 order book data via WebSockets
                orderbook = await exchange.watch_order_book(SYMBOL)
                ingest_latency_sec = time.time() - start_time
                
                INGESTOR_LATENCY.labels(exchange=exchange_name).observe(ingest_latency_sec)

                update_data = {
                    "exchange": exchange_name,
                    "symbol": SYMBOL,
                    "bids": orderbook.get("bids", [])[:5], # top 5 levels
                    "asks": orderbook.get("asks", [])[:5],
                    "timestamp": int(time.time() * 1000)
                }

                await self.redis_manager.publish_orderbook(update_data)
                
        except Exception as e:
            logger.error(f"Error streaming from {exchange_name}: {e}")
        finally:
            await exchange.close()

    async def run_all(self):
        tasks = [self.stream_orderbook(ex_name) for ex_name in self.exchanges.keys()]
        await asyncio.gather(*tasks)
