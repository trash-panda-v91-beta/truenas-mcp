"""TrueNAS MCP server built on FastMCP."""

import logging
import urllib.parse

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from . import __version__
from .client import TrueNASClient
from .config import config

config.configure_logging()
logger = logging.getLogger(__name__)


@lifespan
async def truenas_lifespan(server):
    """Close the shared TrueNAS client on shutdown."""
    global client
    yield None
    if client is not None:
        await client.close()
        client = None


mcp = FastMCP("truenas", lifespan=truenas_lifespan)

# Shared client instance (initialized on first use)
client: TrueNASClient | None = None


async def get_client() -> TrueNASClient:
    """Get the shared TrueNAS client, creating it on first use."""
    global client
    if client is None:
        client = TrueNASClient()
    return client


def _error_text(tool_name: str, exc: Exception) -> str:
    """Map an exception to a user-friendly error message."""
    return f"{tool_name} failed: {exc}"


# MCP tools (disks, pools, apps, VMs, shares, ...) land here - see AGENTS.md.


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info(f"Starting TrueNAS MCP Server v{__version__}")
    logger.info(f"Connecting to: {sanitize_url(config.truenas_base_url or '')}")
    # transport comes from FASTMCP_* env vars (default stdio); blocks until the server stops
    mcp.run()


def sanitize_url(url: str) -> str:
    """Sanitize URL for logging by hiding host details."""
    try:
        parsed = urllib.parse.urlparse(url)
        return f"{parsed.scheme}://[SERVER]{parsed.path}"
    except Exception:
        return "[URL]"


if __name__ == "__main__":
    main()
