"""Configuration management for TrueNAS MCP server."""

import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Environment-driven configuration (reads .env and TRUENAS_* vars)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    truenas_uri: str | None = None
    truenas_api_key: str | None = None
    truenas_verify_ssl: bool = True
    log_level: str = "INFO"

    @field_validator("truenas_uri")
    @classmethod
    def _validate_uri(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v.startswith("wss://") or v.startswith("ws://"):
            return v.rstrip("/")
        raise ValueError("TRUENAS_URI must be a ws:// or wss:// websocket URL, e.g. wss://truenas/api/current")

    def _errors(self) -> list[str]:
        errs: list[str] = []
        if not self.truenas_uri:
            errs.append("TRUENAS_URI is required: ws(s)://<host>/api/current")
        if not self.truenas_api_key:
            errs.append("TRUENAS_API_KEY is required (TrueNAS API Keys)")
        if self.truenas_uri and not self.truenas_verify_ssl and self.truenas_uri.startswith("wss://"):
            errs.append("TRUENAS_VERIFY_SSL=false is not allowed over wss:// - use ws:// or leave verification on")
        return errs

    def validate(self) -> None:
        errs = self._errors()
        if errs:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errs))

    def configure_logging(self) -> None:
        """Configure logging based on log level."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Global configuration instance
config = Config()
