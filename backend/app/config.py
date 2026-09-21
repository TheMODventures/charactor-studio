from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Character Studio"
    database_url: str = "sqlite:///./data/app.db"
    assets_dir: Path = Path("assets")
    model_weights_dir: Path = Path("model_weights")
    ollama_url: str = "http://127.0.0.1:11434"
    dialogue_model: str = "qwen3:8b"
    speech_url: str = ""
    video_url: str = ""
    provider_token: str = ""
    provider_timeout: int = 1800
    worker_poll_seconds: float = 2
    seed_characters: bool = True


settings = Settings()
