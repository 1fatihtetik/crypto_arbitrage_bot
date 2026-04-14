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
