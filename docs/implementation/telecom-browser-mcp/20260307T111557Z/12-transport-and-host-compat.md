# 12 Transport and Host Compatibility

## What Codex changed
- Added server entrypoints:
  - `server/stdio_server.py` (required default)
  - `server/streamable_http_server.py` (preferred remote)
  - `server/sse_server.py` (compatibility path)
- Added host setup docs:
  - `docs/guides/host-setup.md`

## What Codex intentionally did not change
- Did not perform live MCP Inspector/network transport validation in this sandbox run.

## Tests run
- `python -m pytest -q tests/e2e/test_stdio_smoke.py`

## Evidence produced
- Local stdio dispatch smoke assertions.

## Open risks
- Transport-specific behavior can vary by host SDK versions and deployment constraints.

## Next recommended batch
- batch-09-transport-compat.md
