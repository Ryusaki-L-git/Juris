"""
core/config.py — JURIS centralised application settings.

All configuration is read from environment variables and / or a .env file.
No secrets are hardcoded here.

Usage anywhere in the application:
    from core.config import settings
    print(settings.env)
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    JURIS application settings.

    Values are loaded (in priority order) from:
      1. Real environment variables
      2. .env file at the project root
      3. Defaults defined here

    Add new configuration here — never in source code directly.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="JURIS_",
        case_sensitive=False,
        extra="ignore",  # silently ignore unknown env vars
    )

    # ── Application ──────────────────────────────────────────────────────────
    env: Literal["development", "staging", "production"] = "development"
    version: str = "0.2.0"
    debug: bool = False

    # ── API ──────────────────────────────────────────────────────────────────
    api_prefix: str = ""
    # Stored as a raw comma-separated string so pydantic-settings does not
    # attempt JSON decoding before we can parse it.
    # Always access origins via the `allowed_origins` property.
    allowed_origins_raw: str = "http://localhost"

    @property
    def allowed_origins(self) -> list[str]:
        """Return CORS origins as a list, parsed from the comma-separated env var."""
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]

    # ── Model Gateway ─────────────────────────────────────────────────────────
    gateway: Literal["echo"] = "echo"
    # Expand Literal when real providers are wired: "gemini" | "openai" | ...
    # Provider API keys are read here but never logged or exposed via the API.
    gemini_api_key: str = ""

    # ── LED Integration ───────────────────────────────────────────────────────
    led_api_url: str = ""
    # Blank until the LED↔JURIS integration phase.

    # ── eCourts (read-only) ───────────────────────────────────────────────────
    ecourts_base_url: str = ""
    ecourts_api_key: str = ""

    # ── Firebase / Auth ───────────────────────────────────────────────────────
    auth_mode: Literal["firebase", "dev"] = "dev"
    # "firebase": verifies incoming JWT against Firebase Auth.
    # "dev": allows local dev tokens for testing without Firebase.
    # In production/staging, "dev" is strictly forbidden.
    dev_allow_unauthenticated: bool = True
    # If True and in development mode, requests lacking an Authorization
    # header will be assigned a development fallback user (is_verified=False).
    # If False or in staging/production, missing auth yields HTTP 401.
    firebase_project_id: str = ""

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_auth_enforced(self) -> bool:
        """True if authentication is strictly enforced (non-dev or unauthenticated disabled)."""
        return not self.is_development or not self.dev_allow_unauthenticated


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.

    Uses lru_cache so the .env file is read exactly once per process.
    In tests, call get_settings.cache_clear() to reload settings.
    """
    return Settings()


# Module-level convenience alias.
# Prefer importing this directly: `from core.config import settings`
settings: Settings = get_settings()
