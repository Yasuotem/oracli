from pydantic_settings import BaseSettings, SettingsConfigDict

from oracli.types import DbKind


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ORACLI_",
    )
    db: DbKind
    user: str | None = None
    dsn: str | None = None
    password: str | None = None

    path: str | None = None
