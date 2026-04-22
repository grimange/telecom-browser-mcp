# Release Security Summary

## Hardened

- HTTP/SSE non-local bind protection with explicit unsafe-bind opt-in and bearer token requirement.
- Initial and routed browser HTTP/HTTPS request governance using the repo URL policy.
- Central evidence redaction for JSON/HTML artifacts.
- Screenshot suppression by default for non-harness targets plus manifest sensitivity metadata.
- Tightened schema bounds and fail-closed lifecycle behavior from the prior hardening passes.

## Verified

- Unit, contract, transport-entrypoint, registration, Ruff, and Bandit checks pass in the current environment.
- Non-live transport smoke paths truthfully classify constrained-runtime failures as environment limitations.
- Real-host stdio, HTTP, and SSE smoke verification passed on a host-capable runtime.
- Non-local HTTP/SSE fail-closed startup behavior and bearer-token enforcement were verified on the host.

## Residual

- Browser-internal traffic not surfaced through Playwright routing is not claimed as governed.
- Screenshot pixel redaction is not implemented and remains intentionally residual.
- Live stdio/SSE/HTTP runtime verification still requires a host-capable runtime with subprocess and loopback socket support.

## Operator Configuration Required

- Keep HTTP/SSE on localhost by default.
- For non-local HTTP/SSE, set both `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`.
- Configure `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real targets.
- Use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only for explicit harness/local-target testing.
- Enable `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS=1` only when sensitive visual artifacts can be handled securely.

## Compatibility-Impacting Strictness

- Unsafe `open_app` targets fail closed.
- Routed browser requests that violate URL policy are aborted and surfaced as structured `security_policy` failures.
- Non-local HTTP/SSE startup without explicit auth/unsafe-bind configuration fails closed.

## Bounded Release Status

- Current bounded release verdict: `READY_FOR_BOUNDED_RELEASE`
- Supporting evidence: `docs/live-verification-environment-notes.md` and `docs/live-transport-verification-verdict.md`
