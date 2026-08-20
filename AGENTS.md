# truenas-mcp

Model Context Protocol (MCP) server for TrueNAS (SCALE). Exposes the TrueNAS REST API v2.0 as
MCP tools (disks, pools, apps, VMs, shares, datasets, ...) with API-key auth, token-bucket rate
limiting, and connection pooling. Stack and versions live in `pyproject.toml` and `server.py` -
read those for the current shape, don't trust this file.

## Common Tasks

```bash
mise run check    # hk: ruff, actionlint, yamllint, yamlfmt, pkl
mise run fix      # hk fix: auto-fix the same
mise run test     # uv run --extra dev pytest
```

`mise run` is the command surface - use it for everything; no direct tool invocation. New tool /
model / API method flow lives in the `add-tool` skill. Run `mise install` once to get the toolchain
(uv, ruff, hk, ...).

## Release

Merging to `main` triggers `.github/workflows/release.yml` (release-please-action v4): it opens a
`release: vX.Y.Z` PR from Conventional Commits. Merge that PR to cut a release - release-please
bumps the version in `pyproject.toml` + README, tags it, and updates `CHANGELOG.md`. Config lives in
`.release-please-config.json` / `.release-please-manifest.json`.

- Conventional commits drive the version bump and changelog; `chore` is hidden, breaking changes
  bump major.
- Multi-change PRs: use footer syntax (one conventional-commit stanza per change) so each lands as
  its own changelog entry.

## Layout

- `src/truenas_mcp/server.py` - all MCP tools (async funcs with `@mcp.tool` + `_guard`)
- `src/truenas_mcp/client.py` - httpx API client (rate limiting, retry, auth)
- `src/truenas_mcp/models.py` - Pydantic request/response models (add as tools land)
- `src/truenas_mcp/config.py` - env-driven config
- `tests/` - pytest suite (mocked + `live_api` integration)
- `.agents/skills/add-tool/` - repo-local skill for adding a tool

## Conventions

- API-key auth: `Authorization: Bearer <key>` header against `/api/v2.0/`
- Lists are `GET /api/v2.0/<resource>` (paginated via `?limit=&offset=`); single reads and
  mutations use the resource name in the path
- MCP tools return JSON strings via `json.dumps(...)`
- Ad-hoc analysis scripts go in `tmp/` (gitignored); formal tests go in `tests/`
- Don't create `docs/adr/` or `CONTEXT.md`; repo metadata stays out-of-tree
- Commit messages use Conventional Commits: `feat`, `fix`, `chore`, `refactor`, `docs`, `ci`, ...
  Scope optional (e.g. `fix(list_disks): ...`). release-please drives versioning + changelog from
  these.

## Domain

- TrueNAS SCALE REST API v2.0; resources include disks, pools, datasets, shares (SMB/NFS),
  apps (k3s), VMs, network interfaces, users, groups, reporting
- TrueNAS uses API keys (long-lived) - no username/password in the MCP server
- Full API reference: https://api.truenas.com

## Links

- Repo: git@github.com:trash-panda-v91-beta/truenas-mcp.git
