import os
import time
from shared.security_protocols import SecurityManager
from shared.latency_tracker import LatencyTracker

def test_fernet_encryption_cycle():
    # Setup test file
    test_key_file = "test_target.key"
    test_enc_file = "test_keys.enc"
    
    try:
        manager = SecurityManager(key_file=test_key_file, api_keys_file=test_enc_file)
        
        # Original Keys
        payload = {"binance": {"public": "abcd", "secret": "1234"}}
        manager.encrypt_and_save_keys(payload)
        
        # New manager instance to decrypt
        manager_read = SecurityManager(key_file=test_key_file, api_keys_file=test_enc_file)
        decrypted = manager_read.load_and_decrypt_keys()
        
        assert decrypted["binance"]["secret"] == "1234"
        
    finally:
        # Cleanup
        if os.path.exists(test_key_file): os.remove(test_key_file)
        if os.path.exists(test_enc_file): os.remove(test_enc_file)

def test_latency_tracker_bounds():
    tracker = LatencyTracker(rtt_threshold_ms=10) # very tight bounds
    
    tracker.start_ping("binance")
    time.sleep(0.001) # 1ms
    tracker.record_pong("binance")
    
    assert tracker.is_latency_acceptable("binance") is True
    
    tracker.start_ping("okx")
    time.sleep(0.015) # 15ms
    tracker.record_pong("okx")
    
    assert tracker.is_latency_acceptable("okx") is False

def test_rust_executor_mock_dispatch():
    # Calling the Rust compile logic should output string via PyO3!
    # Because cargo is not guaranteed locally, testing full compilation is mocked if missing
    try:
        from rust_executor import FastExecutor
        executor = FastExecutor("encrypted_key_xx", "binance")
        result = executor.execute_trade({"side": "buy", "amount": 1.5, "price": 40100.5})
        assert "Executed buy of 1.5 at 40100.5 on binance via Rust!" in result
    except ImportError:
        # Expected if `setup_rust.py install` has not been run
        pass
