"""TrueNAS client via the official truenas_api_client websocket library.

Opens ONE persistent websocket connection to the TrueNAS middleware (JSON-RPC
over wss) and authenticates with an API key via auth.login_with_api_key.
TrueNAS rate-limits auth attempts aggressively and recommends a persistent
connection, so the client is opened once in the server lifespan and reused.

TrueNAS closes idle websocket connections (~60s), so a background keepalive
task pings core.ping every 30s and reopens the socket if the connection was
lost. The library is synchronous (blocking socket in a daemon thread), so every
call is bridged to the async loop with asyncio.to_thread.
"""

import asyncio
import logging
from typing import Any

from truenas_api_client import Client

from .config import config

logger = logging.getLogger(__name__)

KEEPALIVE_INTERVAL = 30


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
        self._keepalive_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Open the websocket and authenticate. Idempotent."""
        if self._client is not None:
            return

        def _open() -> Client:
            c = Client(uri=self.uri, verify_ssl=self.verify_ssl)
            if not c.call("auth.login_with_api_key", self.api_key):
                raise RuntimeError("auth.login_with_api_key failed - check TRUENAS_API_KEY")
            return c

        try:
            self._client = await asyncio.to_thread(_open)
        except Exception as exc:  # noqa: BLE001
            logger.warning("TrueNAS connect failed: %s", exc)
            self._client = None
            raise
        logger.info("Connected and authenticated to TrueNAS")
        if self._keepalive_task is None:
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _reopen(self) -> None:
        """Close and reopen the websocket (after a lost connection)."""
        old = self._client
        self._client = None
        if old is not None:
            try:
                await asyncio.to_thread(old.close)
            except Exception:  # noqa: BLE001
                pass
        await self.connect()

    async def _keepalive_loop(self) -> None:
        while True:
            await asyncio.sleep(KEEPALIVE_INTERVAL)
            try:
                await self.call("core.ping")
            except Exception as exc:  # noqa: BLE001
                logger.warning("TrueNAS keepalive failed (%s); reconnecting", exc)
                try:
                    await self._reopen()
                except Exception as exc2:  # noqa: BLE001
                    logger.error("TrueNAS reconnect failed: %s", exc2)

    async def close(self) -> None:
        if self._keepalive_task is not None:
            self._keepalive_task.cancel()
            self._keepalive_task = None
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
