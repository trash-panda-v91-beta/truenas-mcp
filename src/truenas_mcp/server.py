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
    global client
    try:
        state = TrueNASClient()
        await state.connect()
        client = state
    except Exception as exc:  # noqa: BLE001 - surface as server startup failure
        logger.error("Failed to connect to TrueNAS: %s", exc)
        client = None
    yield None
    if client is not None:
        await client.close()
        client = None


mcp = FastMCP("truenas", lifespan=truenas_lifespan)

# Shared client instance (opened in lifespan)
client: TrueNASClient | None = None


async def get_client() -> TrueNASClient:
    """Get the shared TrueNAS client, raising if the server could not connect."""
    global client
    if client is None:
        raise RuntimeError("TrueNAS connection unavailable at startup - check TRUENAS_URI/API_KEY")
    return client


def _error_text(tool_name: str, exc: Exception) -> str:
    return f"{tool_name} failed: {exc}"


def _dump(data) -> str:
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Read tools (Type-safe surface over the common middleware .query methods)
# ---------------------------------------------------------------------------


@mcp.tool()
async def system_info() -> str:
    """Get TrueNAS system information (version, hostname, uptime, CPU, memory).

    Returns:
        JSON string with system.info fields.
    """
    try:
        c = await get_client()
        info = await c.call("system.info")
        return _dump(info)
    except Exception as exc:  # noqa: BLE001
        return _error_text("system_info", exc)


@mcp.tool()
async def list_pools(name: str | None = None) -> str:
    """List storage pools and their ZFS status (health, capacity, topology).

    Args:
        name: Restrict to one pool by name (optional).
    """
    try:
        flt = [["name", "=", name]] if name else []
        pools = await (await get_client()).call("pool.query", flt)
        return _dump(pools)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_pools", exc)


@mcp.tool()
async def list_disks(serial: str | None = None) -> str:
    """List disks and their health fields (model, serial, size, SMART status).

    Args:
        serial: Restrict to one disk by serial number (optional).
    """
    try:
        flt = [["serial", "=", serial]] if serial else []
        disks = await (await get_client()).call("disk.query", flt)
        return _dump(disks)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_disks", exc)


@mcp.tool()
async def list_datasets(path: str | None = None) -> str:
    """List ZFS datasets (name, mountpoint, used/available, quotas).

    Args:
        path: Restrict to one dataset by path, e.g. tank/data (optional).
    """
    try:
        flt = [["name", "=", path]] if path else []
        ds = await (await get_client()).call("pool.dataset.query", flt)
        return _dump(ds)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_datasets", exc)


@mcp.tool()
async def list_apps() -> str:
    """List installed applications (k3s apps) with state and version."""
    try:
        apps = await (await get_client()).call("app.query", [])
        return _dump(apps)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_apps", exc)


@mcp.tool()
async def list_vms() -> str:
    """List virtual machines with their current status."""
    try:
        vms = await (await get_client()).call("vm.query", [])
        return _dump(vms)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_vms", exc)


# ---------------------------------------------------------------------------
# Generic escape hatch (covers anything not wrapped above)
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_snapshots(dataset: str | None = None) -> str:
    """List ZFS snapshots.

    Args:
        dataset: Restrict to snapshots of one dataset, e.g. tank/data (optional).
    """
    try:
        flt = [["dataset", "=", dataset]] if dataset else []
        snaps = await (await get_client()).call("pool.snapshot.query", flt)
        return _dump(snaps)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_snapshots", exc)


@mcp.tool()
async def list_shares(kind: str = "smb") -> str:
    """List SMB or NFS shares.

    Args:
        kind: "smb" or "nfs" (default smb).
    """
    try:
        if kind == "nfs":
            shares = await (await get_client()).call("sharing.nfs.query", [])
        else:
            shares = await (await get_client()).call("sharing.smb.query", [])
        return _dump(shares)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_shares", exc)


@mcp.tool()
async def list_alerts() -> str:
    """List TrueNAS system alerts."""
    try:
        alerts = await (await get_client()).call("alert.list")
        return _dump(alerts)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_alerts", exc)


@mcp.tool()
async def get_scrub_status(pool_name: str | None = None) -> str:
    """Get ZFS pool scrub status/schedules.

    Args:
        pool_name: Restrict to one pool by name (optional).
    """
    try:
        flt = [["pool_name", "=", pool_name]] if pool_name else []
        scrubs = await (await get_client()).call("pool.scrub.query", flt)
        return _dump(scrubs)
    except Exception as exc:  # noqa: BLE001
        return _error_text("get_scrub_status", exc)


@mcp.tool()
async def list_boot_environments() -> str:
    """List boot environments (active, activated, kernel/initramfs)."""
    try:
        bes = await (await get_client()).call("boot.environment.query", [])
        return _dump(bes)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_boot_environments", exc)


@mcp.tool()
async def list_jobs(state: str | None = None) -> str:
    """List middleware jobs (long-running operations).

    Args:
        state: Filter by job state, e.g. RUNNING, SUCCESS, FAILED (optional).
    """
    try:
        flt = [["state", "=", state]] if state else []
        jobs = await (await get_client()).call("core.get_jobs", flt)
        return _dump(jobs)
    except Exception as exc:  # noqa: BLE001
        return _error_text("list_jobs", exc)


@mcp.tool()
async def truenas_call(method: str, params: list | None = None) -> str:
    """Call any TrueNAS middleware endpoint directly.

    Args:
        method: Middleware method name, e.g. "pool.query", "user.query",
            "service.query", "alert.list".
        params: JSON array of positional arguments passed to the method. Most
            .query methods take [[filters]], e.g. [[["name","=","tank"]]].
    """
    try:
        params = params or []
        result = await (await get_client()).call(method, *params)
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
