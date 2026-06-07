from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("HARMONYMIND_APP_NAME", "HarmonyMind API")
    app_version: str = os.getenv("HARMONYMIND_APP_VERSION", "0.1.0")
    environment: str = os.getenv("HARMONYMIND_ENV", "local")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
