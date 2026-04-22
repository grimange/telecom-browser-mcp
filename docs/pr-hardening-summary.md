# PR Hardening Summary

## What Changed

- Hardened HTTP/SSE startup so non-local binds fail closed unless `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN` are both set.
- Added strict initial and routed browser URL governance for HTTP/HTTPS requests surfaced through Playwright routing.
- Centralized evidence redaction for JSON/HTML artifacts and tightened screenshot handling for non-harness targets.
- Clarified APNTalk as contract scaffold only and preserved fail-closed behavior for unsupported operations.
- Tightened schema bounds and lifecycle behavior without changing public MCP tool names or envelope shapes.
- Added release-readiness, residual, and live-verification documentation plus host verification helper commands.

## Why It Changed

- Reduce unsafe network exposure for HTTP/SSE transports.
- Prevent `open_app` and routed browser requests from becoming unrestricted local-network browsing primitives.
- Lower artifact leakage risk in debug bundles.
- Make support boundaries, residuals, and operator obligations explicit and reviewable.

## What Was Verified

- Unit, contract, transport-entrypoint, registration, Ruff, and Bandit checks passed.
- Host-capable live transport smoke passed for `stdio`, `streamable-http`, and `sse`.
- Non-local HTTP/SSE startup without required opt-in/auth failed closed as designed.
- Protected non-local HTTP/SSE endpoints enforced bearer-token auth as documented.

## What Remains Residual

- Browser request governance is intentionally bounded to requests surfaced through Playwright routing.
- Screenshot pixel redaction is intentionally not implemented.
- Production still depends on operator-managed reverse proxy, firewall policy, token rotation, and outbound egress controls.

## Compatibility Impact

- Unsafe `open_app` targets now fail closed.
- Routed browser requests that violate URL policy are aborted and surfaced as structured `security_policy` failures.
- Non-local HTTP/SSE startup without explicit auth/unsafe-bind configuration fails closed.
- Screenshot capture is disabled by default for non-harness targets unless explicitly enabled.

## Operator Actions Required

- Keep HTTP/SSE on localhost unless remote exposure is intentional.
- For non-local HTTP/SSE, set both `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`.
- Configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets.
- Use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only for harness/local-target testing.
- Treat screenshots as high-risk artifacts and enable them only when secure handling is in place.
