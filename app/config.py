from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env also holds POSTGRES_* keys for docker compose; ignore them here.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str


settings = Settings()
