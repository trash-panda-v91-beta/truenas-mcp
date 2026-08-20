"""Configuration management for TrueNAS MCP server."""

import logging

from pydantic import field_validator, model_validator
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
    def _normalise_uri(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not (v.startswith("wss://") or v.startswith("ws://")):
            raise ValueError("TRUENAS_URI must be a ws:// or wss:// websocket URL, e.g. wss://truenas/api/current")
        return v.rstrip("/")

    @model_validator(mode="after")
    def _check(self) -> Config:
        if not self.truenas_uri:
            raise ValueError("TRUENAS_URI is required: ws(s)://<host>/api/current")
        if not self.truenas_api_key:
            raise ValueError("TRUENAS_API_KEY is required (TrueNAS API Keys)")
        return self

    def configure_logging(self) -> None:
        """Configure logging based on log level."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Global configuration instance
config = Config()
