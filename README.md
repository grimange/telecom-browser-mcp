# telecom-browser-mcp

`telecom-browser-mcp` is a Python MCP server for telecom-aware browser automation and diagnostics.

## M1 tools

- `open_app`
- `list_sessions`
- `close_session`
- `login_agent`
- `wait_for_ready`
- `wait_for_registration`
- `wait_for_incoming_call`
- `answer_call`
- `get_active_session_snapshot`
- `get_peer_connection_summary`
- `collect_debug_bundle`
- `diagnose_answer_failure`

## Support tools

- `health`
- `capabilities`

## Run

```bash
telecom-browser-mcp-stdio
```

## Adapters

- `generic` fallback adapter
- `fake_dialer` deterministic test harness adapter
- `apntalk` telecom adapter scaffold (domain mapped for `apntalk.com` and `app.apntalk.com`)

## Contract

All M1 tool responses use a strict envelope with `meta.contract_version = "v1"`.

Canonical input contracts are defined in
`src/telecom_browser_mcp/contracts/m1_contracts.py`.
Published schemas are generated into `docs/contracts/m1/`.

Generate schemas:

```bash
PYTHONPATH=src python scripts/generate_contract_schemas.py
```

## Fake Dialer Harness

Deterministic scenarios are provided by `tests/e2e/fixtures/fake_dialer.html`:

- `success`
- `missing_answer`
- `answer_fails`
- `no_registration`
- `no_peer`

Run tests:

```bash
pytest -q
```

If Playwright browser binaries are unavailable in the environment, harness e2e tests are skipped.
These tests are marked `host_required`.

## CI

GitHub Actions runs `ruff check src tests` and `pytest -q` on push and pull requests.
