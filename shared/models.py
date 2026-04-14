from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class OrderBookUpdate:
    exchange: str
    symbol: str
    bids: List[Tuple[float, float]]  # [(price, amount), ...]
    asks: List[Tuple[float, float]]
    timestamp: int  # ms timestamp
