from email.message import EmailMessage
from typing import Optional
import aiosmtplib
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_user
        self.password = settings.smtp_pass
        self.use_tls = settings.smtp_use_tls
        self.default_from = settings.smtp_from or (self.username or "no-reply@example.com")

    async def send_email(self, *, to: str, subject: Optional[str], message: str) -> None:
        msg = EmailMessage()
        msg["From"] = self.default_from
        msg["To"] = to
        msg["Subject"] = subject or "Notification"
        msg.set_content(message)

        if self.use_tls and self.port == 465:
            await aiosmtplib.send(
                msg, hostname=self.host, port=self.port,
                username=self.username, password=self.password,
                use_tls=True, timeout=30,
            )
        else:
            await aiosmtplib.send(
                msg, hostname=self.host, port=self.port,
                username=self.username, password=self.password,
                start_tls=self.use_tls, timeout=30,
            )
