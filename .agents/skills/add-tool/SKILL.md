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

Add a method to `TrueNASClient` and call it from the tool via `get_client()`. Use an `httpx` request
against the TrueNAS REST API v2.0. Remember:
- resource lists are GET `/api/v2.0/<resource>`; reads by name are `/id`; mutations use the
  matching POST/PUT/DELETE with the resource name in the path
- respect the rate limiter via the existing `request` method

## 3. Models - `src/truenas_mcp/models.py`

Add Pydantic models for any request/response shapes. Use camelCase field names (TrueNAS JSON).
Add validators for constraints (ranges, enums, formats) matching the existing pattern.

## 4. Tests - `tests/`

Tests live in `tests/unit/` (mocked), `tests/integration/` (full mock workflows), `tests/live/`
(real instance, marked skip_in_ci/live_api).

- `tests/unit/test_client.py` - mock the httpx transport; assert the method hits the right
  URL/method, sends the right fields, and parses the response
- `tests/unit/test_mcp_tools.py` - mock the `TrueNASClient` and assert the tool returns the
  right output for a given input

## Verify

```bash
mise run check   # ruff + yaml + actionlint
mise run test    # pytest
```

Commit style: `feat: <what the tool does>` (e.g. `feat: add list_disks tool`). Since
release-please drives versioning and the changelog from Conventional Commits on `main`, a `feat`
commit bumps the minor version on release.
