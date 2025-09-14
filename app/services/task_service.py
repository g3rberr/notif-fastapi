from uuid import uuid4
from app.services.pubsub import PubSub

class TaskService:
    def __init__(self, bus: PubSub):
        self.bus = bus

    async def publish(self, *, title: str, payload: str | None):
        event_id = str(uuid4())
        await self.bus.publish({"event_id": event_id, "title": title, "payload": payload})
        return event_id
