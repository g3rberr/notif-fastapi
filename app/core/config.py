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

    redis_url: str
    redis_channel: str = "task_events"
    log_level: str = "INFO"

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
