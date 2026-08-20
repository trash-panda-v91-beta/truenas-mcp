"""TrueNAS MCP server built on FastMCP and the trueNAS middleware websocket API.

Tools cover the common read surfaces (pools, disks, datasets, apps, VMs,
system info) plus a generic truenas_call escape hatch that reaches any
middleware endpoint. All calls go through the persistent websocket client.
"""

import json
import logging

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from . import __version__
from .client import TrueNASClient
from .config import config

config.configure_logging()
logger = logging.getLogger(__name__)


@lifespan
async def truenas_lifespan(server):
    """Open the TrueNAS connection on startup, close it on shutdown."""
    state = {}
    try:
        client = TrueNASClient()
        await client.connect()
        state["client"] = client
    except Exception as exc:  # noqa: BLE001 - surface as server startup failure
        logger.error("Failed to connect to TrueNAS: %s", exc)
        state["client"] = None
        state["error"] = str(exc)
    yield state
    if state.get("client") is not None:
        await state["client"].close()


mcp = FastMCP("truenas", lifespan=truenas_lifespan)


def get_client(ctx) -> TrueNASClient:
    """Get the shared client from server state."""
    state = ctx.request_context.lifespan_context
    client = state.get("client")
    if client is None:
        raise RuntimeError(state.get("error", "TrueNAS connection unavailable"))
    return client


def _error_text(tool_name: str, exc: Exception) -> str:
    return f"{tool_name} failed: {exc}"


def _dump(data) -> str:
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Read tools (Type-safe surface over the common middleware .query methods)
# ---------------------------------------------------------------------------


@mcp.tool()
async def system_info(ctx) -> str:
    """Get TrueNAS system information (version, hostname, uptime, CPU, memory).

    Returns:
        JSON string with system.info fields.
    """
    try:
        info = await get_client(ctx).call("system.info")
        return _dump(info)
    except Exception as exc:  # noqa: BLE001
        return _error_text("system_info", exc)


@mcp.tool()
async def list_pools(ctx, name: str | None = None) -> str:
    """List storage pools and their ZFS status (health, capacity, topology).

    Args:
        name: Restrict to one pool by name (optional).
    """
    try:
        flt = [["name", "=", name]] if name else []
        pools = await get_client(ctx).call("pool.query", flt)
        return _dump(pools)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_pools", exc)


@mcp.tool()
async def list_disks(ctx, serial: str | None = None) -> str:
    """List disks and their health fields (model, serial, size, SMART status).

    Args:
        serial: Restrict to one disk by serial number (optional).
    """
    try:
        flt = [["serial", "=", serial]] if serial else []
        disks = await get_client(ctx).call("disk.query", flt)
        return _dump(disks)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_disks", exc)


@mcp.tool()
async def list_datasets(ctx, path: str | None = None) -> str:
    """List ZFS datasets (name, mountpoint, used/available, quotas).

    Args:
        path: Restrict to one dataset by path, e.g. tank/data (optional).
    """
    try:
        flt = [["name", "=", path]] if path else []
        ds = await get_client(ctx).call("pool.dataset.query", flt)
        return _dump(ds)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_datasets", exc)


@mcp.tool()
async def list_apps(ctx) -> str:
    """List installed applications (k3s apps) with state and version."""
    try:
        apps = await get_client(ctx).call("app.query", [])
        return _dump(apps)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_apps", exc)


@mcp.tool()
async def list_vms(ctx) -> str:
    """List virtual machines with their current status."""
    try:
        vms = await get_client(ctx).call("vm.query", [])
        return _dump(vms)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_vms", exc)


# ---------------------------------------------------------------------------
# Generic escape hatch (covers anything not wrapped above)
# ---------------------------------------------------------------------------


@mcp.tool()
async def truenas_call(ctx, method: str, params: list | None = None) -> str:
    """Call any TrueNAS middleware endpoint directly.

    Args:
        method: Middleware method name, e.g. "pool.query", "user.query",
            "service.query", "alert.list".
        params: JSON array of positional arguments passed to the method. Most
            .query methods take [[filters]], e.g. [[["name","=","tank"]]].
    """
    try:
        params = params or []
        result = await get_client(ctx).call(method, *params)
        return _dump(result)
    except Exception as exc:  # noqa: BLE001
        return _error_text("truenas_call", exc)


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info(f"Starting TrueNAS MCP Server v{__version__}")
    # transport comes from FASTMCP_* env vars (default stdio); blocks until stopped
    mcp.run()


if __name__ == "__main__":
    main()
