---
name: add-tool
description: Add a new MCP tool, API method, or model to this server. Use when implementing a new tool, extending the TrueNAS API surface, or "add a tool" / "add an endpoint". Covers the 4-place pipeline (tool, client method, models, tests).
---

# Add a Tool/Endpoint

A new capability touches these spots, in order. Do them all, then run the checks.

## 1. Tool - `src/truenas_mcp/server.py`

Define an async function with `@mcp.tool()` + `@_guard`, returning `json.dumps(...)`. FastMCP builds
the schema from the typed signature + docstring. Read the nearest existing `@mcp.tool` in the file
and copy its shape - this is the source of truth, not this guide.

## 2. Client method - `src/truenas_mcp/client.py`

Add a method to `TrueNASClient` and call it from the tool via `get_client()`
(the shared persistent websocket). Data reads are middleware `.query` methods:
`call("<resource>.query", [[filters]])`. Empty list = all rows; a filter is a
list like `[["name","=","tank"]]`. Long-running operations use `job=True`.
Remember:
- the library is synchronous - every `call` already bridges via
  `asyncio.to_thread`, so your tool stays async and just awaits `client.call`
- reuse the existing persistent connection, never open a new `Client`
- camelCase field names in filter keys and payloads (TrueNAS JSON)

## 3. Models - (rarely needed)

For most tools the middleware already returns clean dicts; `_dump` serializes
them. Only add Pydantic models when you need to reshape or validate a request
payload. camelCase field names (TrueNAS JSON).

## 4. Tests - `tests/`

Tests live in `tests/unit/`. For a tool, mock the `TrueNASClient.call` (or the
`truenas_api_client.Client`) and assert the tool returns the right JSON for a
given input.

## Verify

```bash
mise run check   # ruff + yaml + actionlint
mise run test    # pytest
```

Commit style: `feat: <what the tool does>` (e.g. `feat: add list_disks tool`). Since
release-please drives versioning and the changelog from Conventional Commits on `main`, a `feat`
commit bumps the minor version on release.
