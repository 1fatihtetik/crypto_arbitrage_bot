import os

# Exchanges to stream from
EXCHANGES = ["binance", "kraken", "okx"]
SYMBOL = "BTC/USDT"

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM_NAME = "orderbooks"

# Safety Manager
KILL_SWITCH_TIMEOUT_MS = 500

# Prometheus
METRICS_PORT = 8000

# Security Protocols
IP_WHITELIST = os.getenv("IP_WHITELIST", "127.0.0.1,192.168.1.1").split(",")
ENFORCE_TRADE_ONLY = True  # Ensure bot cannot call withdrawal endpoints
REQUIRE_ENCRYPTED_KEYS = True
