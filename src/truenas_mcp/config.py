"""Configuration management for TrueNAS MCP server."""

import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Environment-driven configuration (reads .env and TRUENAS_* vars)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    truenas_base_url: str | None = None
    truenas_api_key: str | None = None
    log_level: str = "INFO"
    # Opt into plaintext http base URLs (e.g. cluster-internal .svc.cluster.local).
    # Default stays https-only so the API key is never sent in clear.
    allow_insecure_http: bool = False

    @model_validator(mode="after")
    def _validate(self) -> Config:
        base = self.truenas_base_url or ""
        errors: list[str] = []
        if not base:
            errors.append(
                "TRUENAS_BASE_URL environment variable is required. Please set it to your TrueNAS instance URL."
            )
        elif not base.startswith("https://") and not self.allow_insecure_http:
            errors.append(
                f"TRUENAS_BASE_URL must use HTTPS for security (or set ALLOW_INSECURE_HTTP=true). Got: {base[:50]}"
            )
        if not self.truenas_api_key:
            errors.append("TRUENAS_API_KEY environment variable is required. Generate one in TrueNAS (API Keys).")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        self.truenas_base_url = base.rstrip("/")
        return self

    def configure_logging(self) -> None:
        """Configure logging based on log level."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Global configuration instance
config = Config()
