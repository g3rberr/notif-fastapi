import json, asyncio, random
from uuid import UUID
from datetime import datetime, timedelta, timezone
from celery import Task
from aiosmtplib.errors import SMTPException, SMTPResponseException
import aiosmtplib
from app.services.celery_app import celery
from app.services.email_service import EmailService
from app.repositories.task_repo import TaskRepository
from app.db.session import SessionLocal
from app.core.config import settings

email_service = EmailService()

def calc_backoff(attempt: int) -> float:
    base = settings.backoff_base_sec
    cap = settings.backoff_cap_sec
    delay = min(base * (2 ** (attempt - 1)), cap)
    jitter = delay * settings.backoff_jitter_frac
    return max(0.0, delay + random.uniform(-jitter, jitter))

class DBTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = False
    retry_jitter = False


def is_permanent_smtp_error(exc: Exception) -> tuple[bool, str]:
    if isinstance(exc, SMTPResponseException):
        code = exc.code or 0
        if 500 <= code < 600:
            return True, f"SMTP {code} {exc.message!s}"
        if 400 <= code < 500:
            return False, f"SMTP {code} {exc.message!s}"
    if isinstance(exc, SMTPException):
        return False, exc.__class__.__name__

    msg = str(exc).lower()
    if "rate limit" in msg or "too many requests" in msg or "429" in msg:
        return False, str(exc)

    return False, str(exc)


@celery.task(bind=True, base=DBTask, name="send_email_task", max_retries=settings.max_attempts-1)
def send_email_task(self, task_id: str, payload: str):
    loop = asyncio.get_event_loop()

    async def process():
        async with SessionLocal() as session:
            repo = TaskRepository(session)
            await repo.ensure_processing(UUID(task_id), title="send_email",
                                 payload=payload, worker_id=self.request.hostname)
            try:
                data = json.loads(payload)
                await email_service.send_email(
                    to=data["to"], subject=data.get("subject"), message=data["message"]
                )
                await repo.set_done(UUID(task_id))
            except Exception as exc:
                permanent, reason = is_permanent_smtp_error(exc)
                if permanent:
                    await repo.set_failed(UUID(task_id), last_error=reason)
                    return
                attempt_next = (self.request.retries or 0) + 1
                delay = calc_backoff(attempt_next)
                next_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                await repo.schedule_retry(UUID(task_id),
                    attempt_inc=1, last_error=reason, next_attempt_at=next_at
                )
                raise
            
    try:
        loop.run_until_complete(process())
    except Exception as exc:
        if (self.request.retries or 0) >= (settings.max_attempts - 1):
            loop.run_until_complete(_mark_failed(task_id, str(exc)))
        countdown = calc_backoff((self.request.retries or 0) + 1)
        raise self.retry(exc=exc, countdown=countdown)


async def _mark_failed(task_id: str, error: str):
    async with SessionLocal() as session:
        repo = TaskRepository(session)
        await repo.set_failed(UUID(task_id), last_error=error)
