from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    bot_token: str = Field(alias='BOT_TOKEN')
    admin_id: int = Field(alias='ADMIN_ID')
    database_path: str = Field(
        default=str(BASE_DIR / 'beauty_bot.db'),
        alias='DATABASE_PATH',
    )
    project_name: str = Field(default='BeautyBot Pro', alias='PROJECT_NAME')

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
