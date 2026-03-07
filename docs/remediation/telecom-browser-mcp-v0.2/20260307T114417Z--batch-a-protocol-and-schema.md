# Batch A Protocol and Schema (20260307T114417Z)

## Changes
- Added missing v0.2 tools to discovery catalog in `server/stdio_server.py`:
  - `get_environment_snapshot`
  - `diagnose_one_way_audio`
  - `screenshot`
  - `collect_browser_logs`
- Implemented corresponding orchestrator handlers with structured envelopes.
- Added tool-discovery contract test: `tests/unit/test_tool_discovery_contract.py`.

## Rerun evidence
- tool catalog test passes.
- new tools invoke successfully in harness session except `screenshot` returns structured failure when no active browser page exists.

## Status
- partially fixed (screenshot runtime success remains environment/session dependent).
