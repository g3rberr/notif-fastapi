import orjson
from functools import lru_cache
from redis.asyncio import Redis
from app.core.config import settings

class PubSub:
    def __init__(self, redis: Redis, channel: str):
        self.redis = redis
        self.channel = channel
    async def publish(self, event: dict) -> int:
        return await self.redis.publish(self.channel, orjson.dumps(event).decode())
    async def subscribe(self):
        ps = self.redis.pubsub()
        await ps.subscribe(self.channel)
        return ps

@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
