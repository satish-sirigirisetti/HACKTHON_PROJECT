"""Environment-backed application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings shared by the API and supporting services."""

    database_url: str = "sqlite:///./careerai.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    vector_db_path: str = "./vector_index"
    environment: str = "development"
    frontend_origins: str = "http://127.0.0.1:5500,http://localhost:5500"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        """Return configured browser origins as a normalized list."""
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


settings = Settings()