from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "notification-service"
    api_prefix: str = "/api"

    database_url: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_user: str | None = None
    db_pass: str | None = None
    db_name: str | None = None

    redis_url: str = "redis://redis:6379/0"

    log_level: str = "INFO"

    smtp_host: str
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_pass: str | None = None
    smtp_use_tls: bool = True
    smtp_from: str | None = None

    max_attempts: int = 5
    backoff_base_sec: float = 2.0
    backoff_cap_sec: float = 300.0
    backoff_jitter_frac: float = 0.25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        if not all([self.db_host, self.db_port, self.db_user, self.db_pass, self.db_name]):
            raise ValueError("database settings are incomplete")
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
