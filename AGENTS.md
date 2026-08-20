# truenas-mcp

Model Context Protocol (MCP) server for TrueNAS (SCALE). Exposes the TrueNAS
middleware JSON-RPC API over a persistent websocket as MCP tools (pools, disks,
datasets, apps, VMs, ...) with API-key auth. Uses the official
`truenas_api_client` library (pin `TS-25.10.3`). Stack and versions live in
`pyproject.toml` and `server.py` - read those for the current shape, don't
trust this file.

## Common Tasks

```bash
mise run check    # hk: ruff, actionlint, yamllint, yamlfmt, pkl
mise run fix      # hk fix: auto-fix the same
mise run test     # uv run --extra dev pytest
```

`mise run` is the command surface - use it for everything; no direct tool
invocation. New tool / model / API method flow lives in the `add-tool` skill.
Run `mise install` once to get the toolchain (uv, ruff, hk, ...).

## Release

Merging to `main` triggers `.github/workflows/release.yml` (release-please-action
v4): it opens a `release: vX.Y.Z` PR from Conventional Commits. Merge that PR
to cut a release - release-please bumps the version in `pyproject.toml` +
README, tags it, and updates `CHANGELOG.md`. Config lives in
`.release-please-config.json` / `.release-please-manifest.json`.

- Conventional commits drive the version bump and changelog; `chore` is hidden,
  breaking changes bump major.
- Multi-change PRs: use footer syntax (one conventional-commit stanza per
  change) so each lands as its own changelog entry.

## Layout

- `src/truenas_mcp/server.py` - all MCP tools (async funcs with `@mcp.tool`).
  Reads use `<resource>.query`; the generic `truenas_call` tool reaches any
  middleware method.
- `src/truenas_mcp/client.py` - `TrueNASClient`: one persistent
  `truenas_api_client.Client` websocket, API-key auth, calls bridged to the
  event loop via `asyncio.to_thread`.
- `src/truenas_mcp/config.py` - env-driven config (TRUENAS_URI / API_KEY /
  VERIFY_SSL)
- `tests/` - pytest suite
- `.agents/skills/add-tool/` - repo-local skill for adding a tool

## Conventions

- Auth: `client.call("auth.login_with_api_key", api_key)` after opening the
  websocket. No username needed on 25.10.
- Data reads are middleware `.query` methods taking `[[filters]]` as first arg,
  e.g. `call("pool.query", [["name","=","tank"]])`. Empty list = all rows.
- Long-running ops: `call(..., job=True)` blocks until the job completes.
- The library is synchronous - every call goes through `asyncio.to_thread` so
  the async MCP loop stays responsive. Keep the ONE persistent client.
- MCP tools return JSON strings via `json.dumps(...)`.
- Ad-hoc analysis scripts go in `tmp/` (gitignored); formal tests in `tests/`.
- Don't create `docs/adr/` or `CONTEXT.md`; repo metadata stays out-of-tree.
- Commit messages use Conventional Commits: `feat`, `fix`, `chore`, `refactor`,
  `docs`, `ci`, ... Scope optional (e.g. `fix(list_disks): ...`).

## Domain

- TrueNAS middleware API over websocket (JSON-RPC v2); resources include pools,
  datasets, disks, apps (k3s), VMs, shares, users, groups, services, alerts
- API keys (long-lived); the client connects to `ws(s)://<host>/api/current`
- Version-locked: `truenas_api_client` must match the TrueNAS release
  (targeting 25.10 -> `TS-25.10.3`)

## Links

- Repo: git@github.com:trash-panda-v91-beta/truenas-mcp
- TrueNAS docs: https://api.truenas.com
