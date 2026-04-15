import asyncio
import json
import logging
from typing import Dict
from shared.redis_client import RedisManager
from shared.safety_manager import SafetyManager
from shared.latency_tracker import LatencyTracker
from strategies.regime_detection import RegimeDetectionEngine
from shared.metrics import NET_PROFIT

logger = logging.getLogger("SpatialArbitrage")

class SpatialArbitrageEngine:
    def __init__(self, redis_manager: RedisManager, safety_manager: SafetyManager):
        self.redis = redis_manager
        self.safety_manager = safety_manager
        self.latency_tracker = LatencyTracker(rtt_threshold_ms=100)
        self.regime_engine = RegimeDetectionEngine()
        
        self.latest_books: Dict[str, dict] = {}
        # Fees and slippage assumptions
        self.ASSUMED_FEE_RATE = 0.001
        self.ASSUMED_SLIPPAGE = 0.5 

    def calculate_arbitrage(self):
        if len(self.latest_books) < 2:
            return

        exchanges = list(self.latest_books.keys())
        for i in range(len(exchanges)):
            for j in range(len(exchanges)):
                if i == j:
                    continue

                buy_ex = exchanges[i]
                sell_ex = exchanges[j]

                buy_book = self.latest_books[buy_ex]
                sell_book = self.latest_books[sell_ex]

                if not buy_book.get("asks") or not sell_book.get("bids"):
                    continue

                best_ask_price = buy_book["asks"][0][0]
                best_bid_price = sell_book["bids"][0][0]

                # Net Profit = (Price_Sell - Price_Buy) - (Fees_Total + Slippage)
                fee_total = (best_ask_price * self.ASSUMED_FEE_RATE) + (best_bid_price * self.ASSUMED_FEE_RATE)
                gross_profit = best_bid_price - best_ask_price
                net_profit = gross_profit - fee_total - self.ASSUMED_SLIPPAGE

                if net_profit > 0:
                    # Let's say we have an open websocket ping, check latency
                    if not (self.latency_tracker.is_latency_acceptable(buy_ex) and self.latency_tracker.is_latency_acceptable(sell_ex)):
                        logger.warning(f"Skipping arbitrage due to high latency on {buy_ex} or {sell_ex}")
                        continue
                    
                    logger.info(f"Arbitrage Found! Buy on {buy_ex} @ {best_ask_price}, Sell on {sell_ex} @ {best_bid_price} | Net Profit: {net_profit:.2f}")
                    NET_PROFIT.labels(buy_exchange=buy_ex, sell_exchange=sell_ex).observe(net_profit)

    async def run(self):
        last_id = "$"  # Tail the stream
        while True:
            try:
                # Check kill switch state
                if not self.safety_manager.check_health():
                    # If health fails, skip trading logic
                    await asyncio.sleep(1)
                    continue

                results = await self.redis.get_stream_iterator(last_id=last_id, block=100)
                if not results:
                    continue

                for stream_name, messages in results:
                    for message_id, message_data in messages:
                        last_id = message_id
                        data = json.loads(message_data["data"])
                        exchange = data["exchange"]
                        ts = data["timestamp"]
                        
                        self.latest_books[exchange] = data
                        # Keep safety manager updated with last ingested timestamp per exchange
                        self.safety_manager.update_heartbeat(exchange, ts)

                self.calculate_arbitrage()
            
            except Exception as e:
                logger.error(f"Arbitrage Engine Error: {e}")
                await asyncio.sleep(1)
