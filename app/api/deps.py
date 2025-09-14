from functools import lru_cache
from app.core.config import settings
from app.services.pubsub import PubSub, get_redis_client
from app.services.task_service import TaskService

@lru_cache
def _pubsub_singleton() -> PubSub:
    redis = get_redis_client()
    return PubSub(redis, settings.redis_channel)

async def get_task_service() -> TaskService:
    return TaskService(_pubsub_singleton())
