# TrueNAS MCP

An MCP server that turns your TrueNAS (SCALE) instance into tools. Manage pools,
disks, datasets, apps, VMs and more from any MCP client. Built on FastMCP and the
official `truenas_api_client` websocket library.

Authenticated with a TrueNAS API key over a persistent websocket connection.
Targets TrueNAS 25.10 (pin: `TS-25.10.3`).

## Run with Docker

You need a TrueNAS instance and an API key (Account Settings > API Keys).

```bash
docker build -t truenas-mcp .
docker run -e TRUENAS_URI=wss://truenas.example.com/api/current \
  -e TRUENAS_API_KEY=your-key \
  truenas-mcp
```

## Settings

| name | default | notes |
| ---- | ------- | ----- |
| `TRUENAS_URI` | - | required, ws:// or wss:// websocket URL, e.g. `wss://host/api/current` |
| `TRUENAS_API_KEY` | - | required, from TrueNAS API Keys |
| `TRUENAS_VERIFY_SSL` | true | set false only over plain `ws://` (disable TLS verification for self-signed) |
| `LOG_LEVEL` | INFO | |

Values can come from a `.env` file in the working directory. API-key auth uses
`auth.login_with_api_key` over the persistent connection (TrueNAS 25.10 SCRAM -
no username needed).

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

`system_info`, `list_pools`, `list_disks`, `list_datasets`, `list_apps`,
`list_vms`, `truenas_call` (generic middleware escape hatch).

## License

MIT
