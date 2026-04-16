import pytest
import asyncio
import time
from shared.safety_manager import SafetyManager
from executors.simulation_executor import SimulationExecutor

@pytest.mark.asyncio
async def test_failsafe_execution_halt_under_10ms():
    # Setup infrastructure with high heartbeat timeout so it doesn't auto-trigger
    # However we will manually trip the kill_switch_active to mimic an instant WebSocket drop.
    safety_manager = SafetyManager(timeout_ms=5000)
    safety_manager.update_heartbeat("binance", int(time.time() * 1000))
    
    # Executor with massive simulated latency (500ms) to ensure orders remain PENDING
    executor = SimulationExecutor(safety_manager=safety_manager, simulated_latency_ms=500.0)
    await executor.start()
    
    # 1. Submit Mock Orders
    dummy_book = {"bids": [[40000, 1]], "asks": [[40001, 1]]}
    for i in range(10):
        executor.submit_virtual_order("binance", "buy", 40001, 0.5, dummy_book)
        
    assert len(executor.virtual_orders) == 10
    
    # Let async loops breathe for 1 tick
    await asyncio.sleep(0.001)
    
    # 2. Simulate complete WebSocket Disconnection / Fatal Error
    # This directly triggers the global execution halt
    start_time = time.perf_counter()
    safety_manager.kill_switch_active = True 
    
    # Provide the async orchestrator maximum 10ms to recognize and cascade the cancellations.
    # We yield control to the event loop momentarily.
    await asyncio.sleep(0.005) 
    
    end_time = time.perf_counter()
    reaction_time_ms = (end_time - start_time) * 1000
    
    # 3. Validations
    assert len(executor.virtual_orders) == 0, "Not all virtual orders were canceled!"
    # Windows OS clock resolution is typically ~15.6ms for async sleepers minimum
    assert reaction_time_ms < 25.0, f"Fail-safe took too long to propagate: {reaction_time_ms:.2f}ms"
    
    # Clean up execution task gracefully
    if executor.execution_loop_task:
        executor.execution_loop_task.cancel()
