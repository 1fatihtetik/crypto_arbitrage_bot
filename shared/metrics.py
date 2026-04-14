import time
from prometheus_client import start_http_server, Gauge, Histogram, Counter

# Define metrics
INGESTOR_LATENCY = Histogram(
    'ingestor_latency_seconds',
    'Latency of data ingestion per exchange',
    ['exchange']
)

NET_PROFIT = Histogram(
    'arbitrage_net_profit_usdt',
    'Calculated net profit of arbitrage opportunities',
    ['buy_exchange', 'sell_exchange']
)

KILL_SWITCH_STATUS = Gauge(
    'kill_switch_active',
    'Is the kill switch currently active? (1 = yes, 0 = no)'
)

def start_metrics_server(port: int):
    start_http_server(port)
