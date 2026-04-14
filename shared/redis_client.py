import redis.asyncio as redis
import json
from .config import REDIS_HOST, REDIS_PORT, REDIS_STREAM_NAME

class RedisManager:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    async def publish_orderbook(self, update_data: dict):
        """Publish orderbook update to Redis Stream"""
        await self.redis.xadd(
            REDIS_STREAM_NAME, 
            {"data": json.dumps(update_data)}
        )

    async def get_stream_iterator(self, last_id="$", block=0, count=100):
        """Read from the orderbook stream"""
        return await self.redis.xread({REDIS_STREAM_NAME: last_id}, block=block, count=count)
