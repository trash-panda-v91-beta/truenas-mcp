# Changelog

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
