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

Other transports:

```bash
telecom-browser-mcp-sse
telecom-browser-mcp-http
```

## Adapters

- `generic` fallback adapter
- `fake_dialer` deterministic test harness adapter
- `apntalk` telecom adapter scaffold (domain mapped for `apntalk.com` and `app.apntalk.com`)

## Contract

All M1 tool responses use a strict envelope with `meta.contract_version = "v1"`.

`open_app` also returns `data.ready_for_actions` so clients can gate telecom steps
without probing failures. If `ready_for_actions` is `false`, inspect diagnostics
before calling session-bound telecom actions.

Session-bound operations are serialized per session. If an operation lock cannot
be acquired in time, the tool returns `error.code = "not_ready"` with
`error.classification = "session_busy"` and `retryable = true`.

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

## First-Contact and Workflow

Recommended MCP first-contact sequence:

1. `health`
2. `capabilities`
3. `list_sessions`

Telecom workflow sequence:

1. `open_app`
2. `login_agent`
3. `wait_for_ready`
4. `wait_for_registration`
5. `wait_for_incoming_call`
6. `answer_call`
7. `get_active_session_snapshot` / `get_peer_connection_summary`
8. `collect_debug_bundle` / `diagnose_answer_failure` as needed
9. `close_session`

## CI

GitHub Actions runs `ruff check src tests` and `pytest -q` on push and pull requests.

For host-lane transport proof (require non-skipped stdio/SSE/HTTP smoke), run:

```bash
MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 \
  pytest -q tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py
```

When `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1` is set, environment limitations fail the test run instead of skipping.
