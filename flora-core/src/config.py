from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Flora Core"
    database_url: str = "postgresql+psycopg://flora:flora@localhost:5400/flora"


settings = Settings()
