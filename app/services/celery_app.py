from celery import Celery
from app.core.config import settings

celery = Celery("notification_service",
    broker=settings.redis_url,
    backend=None,
)

celery.conf.update(
    task_default_queue="default",
    task_track_started=False,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_transport_options={"visibility_timeout": 3600},

    broker_pool_limit=200,
    broker_heartbeat=0,
    broker_connection_max_retries=0,
    task_publish_retry=False,

    task_ignore_result=True,
    imports=["app.services.tasks_email"],
)
