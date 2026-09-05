# Changelog

## [0.1.6](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.5...v0.1.6) (2026-09-05)


### Features

* **mise:** update mise tools ([#15](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/15)) ([9b71e6c](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/9b71e6c618a0e99c0d2a78b5a3a77084c606fa82))


### Bug Fixes

* **deps:** update fastmcp ( 4.0.0b3 ➔ 4.0.0b4 ) ([#18](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/18)) ([1ff859d](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/1ff859dc0e21a61182296f280f739811ce9910ef))
* **deps:** update fastmcp ( 4.0.0b4 ➔ 4.0.0b5 ) ([#19](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/19)) ([d1df67e](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/d1df67ea8dfc2ef52bd49692feef3bce9ec774bf))


### Continuous Integration

* **github-action:** update renovatebot/github-action ( v46.2.2 ➔ v46.2.4 ) ([#16](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/16)) ([d5d6f4d](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/d5d6f4dd114209b2aa9f4d8ea14eb469e8782e65))
* **github-action:** update renovatebot/github-action ( v46.2.4 ➔ v46.2.5 ) ([#21](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/21)) ([7c3d9f4](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/7c3d9f422101a6df76e0035e0cf41c3469156f0f))

## [0.1.5](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.4...v0.1.5) (2026-08-20)


### Features

* add read, app management, and storage create/manage tools ([#14](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/14)) ([e9eb9d2](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/e9eb9d2296b74d6f9d110e1e824c7e39bc37675f))


### Bug Fixes

* keep TrueNAS websocket alive (idle connections get closed) ([#11](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/11)) ([e2f40be](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/e2f40be6096a6220d5a43ad5477dd6377b622951))


### Continuous Integration

* add manual workflow_dispatch to publish container image ([#13](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/13)) ([7b3d70d](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/7b3d70d2ab77ce4fba53e09023d20948da43b52d))

## [0.1.4](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.3...v0.1.4) (2026-08-20)


### Bug Fixes

* correct FastMCP tool client access (no spurious ctx param) ([#9](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/9)) ([c43b087](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/c43b0871f84e459755d157ee17928a0058d40845))

## [0.1.3](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.2...v0.1.3) (2026-08-20)


### Bug Fixes

* allow TRUENAS_VERIFY_SSL=false over wss for self-signed certs ([#7](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/7)) ([6cffe36](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/6cffe36187c3cfb23ad6bce030afa1a264277123))

## [0.1.2](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.1...v0.1.2) (2026-08-20)


### Bug Fixes

* install git in builder so uv sync resolves the git dependency ([#5](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/5)) ([7e636f4](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/7e636f47e0d8a2cdd44fdab2e45f23fe277442c1))

## [0.1.1](https://github.com/trash-panda-v91-beta/truenas-mcp/compare/v0.1.0...v0.1.1) (2026-08-20)


### Features

* switch to official truenas_api_client websocket transport ([#4](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/4)) ([66f4c3a](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/66f4c3a856a71d020ceffdd8d618ad5df8b83b3d))


### Bug Fixes

* alphabetic keywords in pyproject for tombi ([#1](https://github.com/trash-panda-v91-beta/truenas-mcp/issues/1)) ([77e9cd0](https://github.com/trash-panda-v91-beta/truenas-mcp/commit/77e9cd0efa35b976ba68fd20548033158e5c5388))
