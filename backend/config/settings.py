# ─────────────────────────────────────────────
#  backend/config/settings.py
#  All environment-driven configuration.
#  Values can be overridden via a .env file.
# ─────────────────────────────────────────────

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME:    str = "Face Attendance API"
    APP_VERSION: str = "1.0.0"
    DEBUG:       bool = False

    # ── Database ──────────────────────────────────────────────────────────────
    # SQLite by default; swap with postgresql+asyncpg://... for production
    DATABASE_URL: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent.parent / 'database' / 'attendance.db'}"

    # ── Auth / JWT ────────────────────────────────────────────────────────────
    SECRET_KEY:            str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM:             str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:  int = 60
    REFRESH_TOKEN_EXPIRE_DAYS:    int = 7

    # ── Desktop API Key ───────────────────────────────────────────────────────
    # The desktop app can also authenticate with a static key (simpler flow)
    DESKTOP_API_KEY: str = "dev-api-key-change-me"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:4173",   # Vite preview
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        extra    = "ignore"


# Single shared instance
settings = Settings()