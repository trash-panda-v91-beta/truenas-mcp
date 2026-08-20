"""TrueNAS API client with API-key auth, rate limiting, and retry.

Authenticates with a TrueNAS API key sent in the `Authorization: Bearer`
header against the REST API v2.0. Concrete endpoint methods (disks, pools,
apps, VMs, ...) are added next - this shell wires up transport, auth header,
and the token-bucket rate limiter shared by every tool.
"""

import asyncio
import logging
import random
import time

import httpx2 as httpx

from .config import config

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        async with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                wait_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(wait_time)


class TrueNASClient:
    """Async client for the TrueNAS REST API v2.0 (API-key auth)."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        rate_limit_per_second: float | None = None,
        rate_limit_burst: int | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or config.truenas_base_url or "").rstrip("/")
        self.api_key = api_key or config.truenas_api_key
        rate = rate_limit_per_second or 10.0
        burst = rate_limit_burst or 10
        self._bucket = TokenBucket(rate, burst)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(timeout),
        )

    async def close(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _headers() -> dict[str, str]:
        return {"Accept": "application/json"}

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Rate-limited request with one retry on transient failure."""
        await self._bucket.acquire()
        try:
            resp = await self._client.request(method, path, headers=self._headers(), **kwargs)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 502, 503, 504):
                await asyncio.sleep(random.uniform(0.2, 0.8))
                return await self._client.request(method, path, headers=self._headers(), **kwargs)
            raise

    # Concrete endpoint methods (disks, pools, apps, VMs, ...) land here.
