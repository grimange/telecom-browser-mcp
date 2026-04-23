# Codex Agent Usage

Prefer stdio transport for local agent work. It avoids exposing an HTTP listener and matches the safest default contract.

Core smoke commands are covered by CI in `.github/workflows/ci.yml`:

```bash
ruff check src tests
python scripts/generate_contract_schemas.py
pytest -q tests/contract tests/integration/test_server_registration.py
pytest -q tests/unit
pytest -q tests/integration/test_transport_entrypoints.py tests/integration/test_stdio_smoke.py tests/integration/test_http_transport_smoke.py
```

For real-host live verification, run the helper script rather than manually reconstructing the command set:

```bash
bash scripts/run_live_transport_smoke.sh stdio
bash scripts/run_live_transport_smoke.sh http
bash scripts/run_live_transport_smoke.sh sse
```

`open_app` only navigates to `http` or `https` targets that pass the egress policy. Configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets. Local/private targets are blocked unless `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` is paired with an explicit allowlist for a harness host.

The same URL policy is installed as a browser request guard for HTTP/HTTPS requests surfaced through Playwright routing. It blocks unsafe redirects, iframe navigations, fetch/XHR, and subresources where Playwright exposes the request. Treat deployment-layer network egress controls as still required for defense in depth.

Evidence bundles are stored below the session artifact root reported by tool responses. Textual artifacts are redacted before write. Screenshots remain sensitive because pixel redaction is not guaranteed; they are disabled by default for non-harness targets unless `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS=1` is set. Bundle manifests record screenshot sensitivity metadata. Do not commit real debug bundles.

APNTalk support status: `login_ui_plus_bridge_observation`. The adapter supports login through the visible UI with bounded selector matching and conservative post-login confirmation. A valid APNTalk runtime bridge can now truthfully back `get_registration_status`, `wait_for_registration`, `wait_for_ready`, `wait_for_incoming_call`, `get_peer_connection_summary`, and bounded `answer_call`/`hangup_call` via the visible main softphone controls only. Store snapshots remain intentionally fail-closed until those selectors or runtime probes are implemented and verified by tests.

Phase 0 APNTalk truth surfaces are now available through `capabilities`, `open_app`, and `get_active_session_snapshot`. These outputs distinguish declared support from real binding status and include bounded early diagnostics such as adapter identity, APNTalk contract gaps, runtime-bridge present/absent status, login-selector observations when checkable, and microphone permission state when the browser safely exposes it.

The consumer-side APNTalk runtime bridge contract is documented in [docs/apntalk-runtime-bridge-contract.md](/home/grimange/personal_projects/telecom-browser-mcp/docs/apntalk-runtime-bridge-contract.md:1). This repo can validate and consume `window.__apnTalkTestBridge` when APNTalk exposes it. In the current bounded pass, that truthfully upgrades bridge-backed registration observation, registration wait observation, ready observation, safe incoming-ringing observation, bounded peer-connection summary observation, and bounded visible-UI answer/hangup only. It does not by itself make store snapshot paths supported.

Security checks can be run locally with:

```bash
pip-audit
bandit -q -r src
ruff check src tests
```

Live transport verification on a capable host:

```bash
bash scripts/run_live_transport_smoke.sh all
```

Secure non-local deployment guidance:

- Keep `FASTMCP_HOST` on localhost unless remote access is intentional.
- For non-local HTTP/SSE binds, set both `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`.
- Rotate `TELECOM_BROWSER_MCP_AUTH_TOKEN` through your existing secret-management path; this repo does not implement token rotation for you.
- Put non-local HTTP/SSE behind reverse proxy and firewall rules that restrict source networks.
- Use host/container outbound egress controls as defense in depth; browser request governance is not a full network policy.
- Use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only for harness/local-target testing, not for real-target operation.
