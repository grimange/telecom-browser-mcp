# Security Hardening

## Transport

- Stdio is the safest/default local transport.
- HTTP/SSE bind to `127.0.0.1` by default.
- Non-local HTTP/SSE requires `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN`.
- Token-protected mode uses the MCP/FastMCP bearer-token verifier when available in the installed stack.

Operational expectations:

- Keep HTTP/SSE on localhost unless remote access is explicitly required.
- Rotate `TELECOM_BROWSER_MCP_AUTH_TOKEN` through external secret-management and deployment rollout; this repo only verifies the configured token value.
- For non-local HTTP/SSE, layer reverse proxy restrictions, firewall policy, and container/network segmentation on top of bearer auth.

## URL Egress

`open_app` validates schemes, host allowlists, DNS results, and unsafe IP ranges before browser navigation. The browser context also installs a Playwright route guard that applies the same policy to HTTP/HTTPS browser requests surfaced by Playwright, including document navigations, redirects, iframe navigations, fetch/XHR, and subresources. Blocked targets return structured `target_url_blocked` errors with `security_policy` classification and sanitized target diagnostics.

Configuration:

- `TELECOM_BROWSER_MCP_ALLOWED_HOSTS`: comma-separated hostnames or glob patterns.
- `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS`: enables explicitly allowlisted localhost/private harness targets.

Residual boundaries: this guard governs requests surfaced through Playwright routing. It does not claim coverage for browser-internal requests that Playwright does not expose, non-HTTP browser internals, or deployment-layer network egress controls.

Defense in depth:

- Use outbound egress controls at the host, VM, container, or cluster layer.
- Treat `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` as harness-only posture, not a production setting.

## Evidence

Evidence artifacts live under `artifacts/<session_id>/<bundle_id>/` by default. JSON and HTML artifacts are redacted centrally before write. Screenshots are sensitive and disabled by default for non-harness targets. Set `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS=1` only when visual capture is required and the output can be protected. Manifest sensitivity metadata records that screenshot pixel redaction is not implemented.

Handling guidance:

- Treat screenshots as high-risk artifacts.
- Do not commit real debug bundles.
- Prefer harness screenshots over real-target screenshots whenever evidence requirements allow it.
