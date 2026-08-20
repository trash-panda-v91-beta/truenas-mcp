"""TrueNAS client via the official truenas_api_client websocket library.

Opens ONE persistent websocket connection to the TrueNAS middleware (JSON-RPC
over wss) and authenticates with an API key via auth.login_with_api_key.
TrueNAS rate-limits auth attempts aggressively and recommends a persistent
connection, so the client is opened once in the server lifespan and reused.

The library is synchronous (blocking socket in a daemon thread), so every call
is bridged to the async loop with asyncio.to_thread.
"""

import asyncio
import logging
from typing import Any

from truenas_api_client import Client

from .config import config

logger = logging.getLogger(__name__)


class TrueNASClient:
    """Persistent websocket connection to TrueNAS middleware (API-key auth)."""

    def __init__(
        self,
        uri: str | None = None,
        api_key: str | None = None,
        verify_ssl: bool | None = None,
    ):
        self.uri = uri or config.truenas_uri or ""
        self.api_key = api_key or config.truenas_api_key
        self.verify_ssl = config.truenas_verify_ssl if verify_ssl is None else verify_ssl
        self._client: Client | None = None

    async def connect(self) -> None:
        """Open the websocket and authenticate. Idempotent."""
        if self._client is not None:
            return

        def _open() -> Client:
            c = Client(uri=self.uri, verify_ssl=self.verify_ssl)
            if not c.call("auth.login_with_api_key", self.api_key):
                raise RuntimeError("auth.login_with_api_key failed - check TRUENAS_API_KEY")
            return c

        self._client = await asyncio.to_thread(_open)
        logger.info("Connected and authenticated to TrueNAS")

    async def close(self) -> None:
        if self._client is None:
            return
        client = self._client
        self._client = None
        await asyncio.to_thread(client.close)

    async def call(self, method: str, *params: Any, job: bool = False, timeout: float | None = None) -> Any:
        """Call a middleware method, bridging the blocking client to the event loop."""
        if self._client is None:
            await self.connect()
        client = self._client
        if client is None:
            raise RuntimeError("TrueNAS client is not connected")
        kwargs = {}
        if job:
            kwargs["job"] = True
        if timeout is not None:
            kwargs["timeout"] = timeout
        return await asyncio.to_thread(client.call, method, *params, **kwargs)
