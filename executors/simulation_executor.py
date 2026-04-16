import asyncio
import time
import logging
import uuid
from typing import Dict, List
from shared.safety_manager import SafetyManager

logger = logging.getLogger("SimulationExecutor")

class VirtualOrder:
    def __init__(self, order_id: str, side: str, price: float, amount: float, timestamp: float):
        self.order_id = order_id
        self.side = side
        self.price = price
        self.amount = amount
        self.timestamp = timestamp
        self.status = "PENDING"
        self.latency_mock_task = None

class SimulationExecutor:
    def __init__(self, safety_manager: SafetyManager, network_latency_ms: float = 20.0, computation_latency_ms: float = 2.0, execution_latency_ms: float = 25.0):
        self.safety_manager = safety_manager
        self.network_latency_ms = network_latency_ms
        self.computation_latency_ms = computation_latency_ms
        self.execution_latency_ms = execution_latency_ms
        self.total_tick_to_trade_ms = network_latency_ms + computation_latency_ms + execution_latency_ms
        self.virtual_orders: Dict[str, VirtualOrder] = {}
        self.execution_loop_task = None
        
    async def start(self):
        """Starts the background task to constantly check SafetyManager for cancellations."""
        self.execution_loop_task = asyncio.create_task(self._failsafe_monitor_loop())

    async def _failsafe_monitor_loop(self):
        """
        Runs continuously. If safety manager engages kill switch, immediately
        cancels all virtual orders to simulate the strict <10ms Fail-Safe constraint.
        """
        while True:
            if not self.safety_manager.check_health():
                self._cancel_all_orders()
            # Sleep very little to ensure <10ms reaction time
            await asyncio.sleep(0.001) 

    def _cancel_all_orders(self):
        canceled = 0
        for order_id, order in list(self.virtual_orders.items()):
            if order.latency_mock_task and not order.latency_mock_task.done():
                order.latency_mock_task.cancel()
            order.status = "CANCELED"
            canceled += 1
            del self.virtual_orders[order_id]
        if canceled > 0:
            logger.warning(f"Fail-Safe triggered! Canceled {canceled} pending virtual orders immediately.")

    async def _process_order_with_latency(self, order: VirtualOrder, target_book_state: dict):
        """Simulates network latency and executes if depth permits."""
        try:
            # 1. Induce Tick-to-Trade delay (Networking + Computation + Execution Latency)
            await asyncio.sleep(self.total_tick_to_trade_ms / 1000.0)
            # 2. Check if order was canceled during latency
            if order.status == "CANCELED" or not self.safety_manager.check_health():
                return
            
            # 3. Simulate Fill Mechanics
            best_bid = target_book_state.get('bids', [[0, 0]])[0][0]
            best_ask = target_book_state.get('asks', [[float('inf'), 0]])[0][0]
            
            fill_price = None
            if order.side == "buy" and order.price >= best_ask:
                fill_price = best_ask
            elif order.side == "sell" and order.price <= best_bid:
                fill_price = best_bid
                
            if fill_price:
                order.status = "FILLED"
                logger.debug(f"Virtual FILL [{order.order_id}] {order.side} @ {fill_price}")
            else:
                order.status = "REJECTED_PRICE_MOVED"
                
            # Cleanup
            if order.order_id in self.virtual_orders:
                del self.virtual_orders[order.order_id]

        except asyncio.CancelledError:
            # Order was canceled halfway through the latency window by the Fail-Safe
            order.status = "CANCELED"

    def submit_virtual_order(self, exchange: str, side: str, price: float, amount: float, book_state: dict) -> str:
        """Entry point for the strategy to test mock executions."""
        if not self.safety_manager.check_health():
            logger.error("Cannot submit order; Safety Manager kill switch is active.")
            return None
            
        order_id = f"virt_{uuid.uuid4().hex[:8]}_{side}"
        order = VirtualOrder(order_id, side, price, amount, time.perf_counter())
        self.virtual_orders[order_id] = order
        
        # Dispatch async task for latency and matching
        task = asyncio.create_task(self._process_order_with_latency(order, book_state))
        order.latency_mock_task = task
        
        return order_id
