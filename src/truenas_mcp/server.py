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


# ---------------------------------------------------------------------------
# Write / management tools (dry_run previews before executing)
# ---------------------------------------------------------------------------


def _preview(op: str, payload, note: str) -> str:
    return _dump({"dry_run": True, "operation": op, "payload": payload, "note": note})


@mcp.tool()
async def install_app(
    app_name: str, catalog_app: str, values: str, train: str = "stable", version: str = "latest", dry_run: bool = True
) -> str:
    """Install an app from the TrueNAS catalog.

    Args:
        app_name: Unique name for the installed app instance (lowercase, no spaces).
        catalog_app: Catalog app id, e.g. "jellyfin" or "custom-app".
        values: JSON string of the app install values/config (the chart values).
        train: Catalog train, default "stable".
        version: App version, default "latest".
        dry_run: Preview only (default True); set False to actually install.
    """
    import json as _json

    try:
        parsed = _json.loads(values)
    except Exception:
        return _error_text("install_app", ValueError("values must be a JSON object string"))
    payload = {"app_name": app_name, "catalog_app": catalog_app, "train": train, "version": version, "values": parsed}
    if dry_run:
        return _preview("app.create", payload, "No app installed. Set dry_run=false to execute.")
    result = await (await get_client()).call("app.create", payload, job=True)
    return _dump({"job": result})


@mcp.tool()
async def start_app(app_name: str) -> str:
    """Start an installed app. Long-running (may take seconds)."""
    try:
        job = await (await get_client()).call("app.start", app_name, job=True)
        return _dump({"job": job})
    except Exception as exc:  # noqa: BLE001
        return _error_text("start_app", exc)


@mcp.tool()
async def stop_app(app_name: str) -> str:
    """Stop an installed app. Long-running (may take seconds)."""
    try:
        job = await (await get_client()).call("app.stop", app_name, job=True)
        return _dump({"job": job})
    except Exception as exc:  # noqa: BLE001
        return _error_text("stop_app", exc)


@mcp.tool()
async def update_app(app_name: str, values: str, dry_run: bool = True) -> str:
    """Update an installed app's configuration.

    Args:
        app_name: Installed app name.
        values: JSON string of updated values/config for the app.
        dry_run: Preview only (default True); set False to apply.
    """
    import json as _json

    try:
        parsed = _json.loads(values)
    except Exception:
        return _error_text("update_app", ValueError("values must be a JSON object string"))
    if dry_run:
        return _preview("app.update", {"app_name": app_name, "values": parsed}, "No update applied. Set dry_run=false.")
    job = await (await get_client()).call("app.update", app_name, {"values": parsed}, job=True)
    return _dump({"job": job})


@mcp.tool()
async def upgrade_app(app_name: str, dry_run: bool = True) -> str:
    """Upgrade an installed app to the latest version.

    Args:
        app_name: Installed app name.
        dry_run: Preview only (default True); set False to upgrade.
    """
    if dry_run:
        return _preview("app.upgrade", {"app_name": app_name}, "No upgrade applied. Set dry_run=false.")
    job = await (await get_client()).call("app.upgrade", app_name, {}, job=True)
    return _dump({"job": job})


@mcp.tool()
async def delete_app(app_name: str, remove_images: bool = False, dry_run: bool = True) -> str:
    """Delete an installed app.

    Args:
        app_name: Installed app name.
        remove_images: Also remove the app's container images.
        dry_run: Preview only (default True); set False to delete.
    """
    if dry_run:
        return _preview(
            "app.delete", {"app_name": app_name, "remove_images": remove_images}, "No app deleted. Set dry_run=false."
        )
    job = await (await get_client()).call("app.delete", app_name, {"remove_images": remove_images}, job=True)
    return _dump({"job": job})


@mcp.tool()
async def search_app_catalog(catalog_app: str = "", train: str = "stable") -> str:
    """Search the TrueNAS app catalog for available apps.

    Args:
        catalog_app: Optional app id to get details for (e.g. "jellyfin").
        train: Catalog train, default "stable".
    """
    try:
        if catalog_app:
            result = await (await get_client()).call("catalog.get_app_details", catalog_app, train)
        else:
            result = await (await get_client()).call("app.available", [["train", "=", train]])
        return _dump(result)
    except Exception as exc:  # noqa: BLE001
        return _error_text("search_app_catalog", exc)


@mcp.tool()
async def create_dataset(name: str, dry_run: bool = True) -> str:
    """Create a ZFS dataset.

    Args:
        name: Full dataset path to create, e.g. "tank/data/apps".
        dry_run: Preview only (default True); set False to create.
    """
    payload = {"name": name, "type": "FILESYSTEM"}
    if dry_run:
        return _preview("pool.dataset.create", payload, "No dataset created. Set dry_run=false.")
    result = await (await get_client()).call("pool.dataset.create", payload)
    return _dump(result)


@mcp.tool()
async def delete_dataset(name: str, recursive: bool = False, dry_run: bool = True) -> str:
    """Delete a ZFS dataset.

    Args:
        name: Dataset path to delete, e.g. "tank/data/apps".
        recursive: Delete child datasets/snapshots too.
        dry_run: Preview only (default True); set False to delete.
    """
    payload = {"recursive": recursive}
    if dry_run:
        return _preview("pool.dataset.delete", {"name": name, **payload}, "No dataset deleted. Set dry_run=false.")
    result = await (await get_client()).call("pool.dataset.delete", [["id", "=", name]], payload)
    return _dump(result)


@mcp.tool()
async def create_snapshot(dataset: str, name: str | None = None, dry_run: bool = True) -> str:
    """Create a ZFS snapshot.

    Args:
        dataset: Dataset to snapshot, e.g. "tank/data".
        name: Optional snapshot name (defaults to auto timestamp).
        dry_run: Preview only (default True); set False to create.
    """
    payload = {"dataset": dataset}
    if name:
        payload["name"] = name
    if dry_run:
        return _preview("pool.snapshot.create", payload, "No snapshot created. Set dry_run=false.")
    result = await (await get_client()).call("pool.snapshot.create", payload)
    return _dump(result)


@mcp.tool()
async def delete_snapshot(name: str, dry_run: bool = True) -> str:
    """Delete a ZFS snapshot.

    Args:
        name: Full snapshot name, e.g. "tank/data@auto-2026-08-20".
        dry_run: Preview only (default True); set False to delete.
    """
    payload = {"name": name}
    if dry_run:
        return _preview("pool.snapshot.delete", payload, "No snapshot deleted. Set dry_run=false.")
    result = await (await get_client()).call("pool.snapshot.delete", payload)
    return _dump(result)


@mcp.tool()
async def create_share(kind: str, name: str, path: str, dry_run: bool = True) -> str:
    """Create an SMB or NFS share.

    Args:
        kind: "smb" or "nfs".
        name: Share name (SMB) or alias (NFS).
        path: Dataset path to share, e.g. "/mnt/tank/stores/petr".
        dry_run: Preview only (default True); set False to create.
    """
    payload = {"name": name, "path": path}
    if kind not in ("smb", "nfs"):
        return _error_text("create_share", ValueError('kind must be "smb" or "nfs"'))
    method = f"sharing.{kind}.create"
    if dry_run:
        return _preview(method, payload, "No share created. Set dry_run=false.")
    result = await (await get_client()).call(method, payload)
    return _dump(result)


@mcp.tool()
async def delete_share(kind: str, share_id: int, dry_run: bool = True) -> str:
    """Delete an SMB or NFS share.

    Args:
        kind: "smb" or "nfs".
        share_id: Share id (from list_shares).
        dry_run: Preview only (default True); set False to delete.
    """
    if kind not in ("smb", "nfs"):
        return _error_text("delete_share", ValueError('kind must be "smb" or "nfs"'))
    method = f"sharing.{kind}.delete"
    if dry_run:
        return _preview(method, {"id": share_id}, "No share deleted. Set dry_run=false.")
    result = await (await get_client()).call(method, share_id)
    return _dump(result)


@mcp.tool()
async def run_scrub(pool_name: str, dry_run: bool = True) -> str:
    """Run a ZFS scrub on a pool.

    Args:
        pool_name: Pool name, e.g. "tank".
        dry_run: Preview only (default True); set False to run.
    """
    payload = {"pool": pool_name}
    if dry_run:
        return _preview("pool.scrub.run", payload, "No scrub started. Set dry_run=false.")
    result = await (await get_client()).call("pool.scrub.run", pool_name)
    return _dump(result)


@mcp.tool()
async def dismiss_alert(alert_id: str) -> str:
    """Dismiss a TrueNAS alert.

    Args:
        alert_id: Alert id (from list_alerts).
    """
    try:
        result = await (await get_client()).call("alert.dismiss", alert_id)
        return _dump(result if result is not None else {"dismissed": True})
    except Exception as exc:  # noqa: BLE001
        return _error_text("dismiss_alert", exc)


@mcp.tool()
async def restore_alert(alert_id: str) -> str:
    """Restore a dismissed TrueNAS alert.

    Args:
        alert_id: Alert id (from list_alerts).
    """
    try:
        result = await (await get_client()).call("alert.restore", alert_id)
        return _dump(result if result is not None else {"restored": True})
    except Exception as exc:  # noqa: BLE001
        return _error_text("restore_alert", exc)


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
