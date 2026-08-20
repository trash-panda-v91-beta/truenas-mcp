# TrueNAS MCP

An MCP server that turns your TrueNAS instance into tools. Manage disks, pools,
apps, VMs, shares and more from any MCP client. Built with FastMCP.

Authenticated with a TrueNAS API key. Tool list and API surface are being
designed - see AGENTS.md for the current shape.

## Run with Docker

You need a TrueNAS instance and an API key (Account Settings > API Keys).

```bash
docker build -t truenas-mcp .
docker run -e TRUENAS_BASE_URL=https://truenas.example.com \
  -e TRUENAS_API_KEY=your-key \
  truenas-mcp
```

## Settings

| name | default | notes |
| ---- | ------- | ----- |
| `TRUENAS_BASE_URL` | - | required, https only |
| `TRUENAS_API_KEY` | - | required, from TrueNAS API Keys |
| `LOG_LEVEL` | INFO | |
| `ALLOW_INSECURE_HTTP` | false | set true for plaintext http base URLs |

Values can come from a `.env` file in the working directory.

## Serve over HTTP

By default the server talks stdio (one process per client). To expose it as an
HTTP MCP endpoint behind a gateway (e.g. LiteLLM), set the FastMCP transport
env vars - no code change required:

| env | default |
| --- | ------- |
| `FASTMCP_TRANSPORT` | `stdio` |
| `FASTMCP_HOST` | `127.0.0.1` |
| `FASTMCP_PORT` | `8000` |
| `FASTMCP_STREAMABLE_HTTP_PATH` | `/mcp` |

Example - serve streamable-http on all interfaces:

```bash
FASTMCP_TRANSPORT=streamable-http FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8000 \
  truenas-mcp
```

## Tools

TBD - tool surface is under design.

## License

MIT
