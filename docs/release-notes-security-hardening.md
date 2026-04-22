# Release Notes: Security Hardening

## Transport Hardening

- HTTP/SSE now default to localhost-only posture.
- Non-local HTTP/SSE startup fails closed unless `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN` are configured.
- Host verification confirmed bearer-token enforcement on protected non-local HTTP/SSE paths.

## URL Egress Policy Hardening

- `open_app` validates scheme, host allowlist, DNS resolution, and unsafe address classes before initial navigation.
- Browser request governance applies the same policy to Playwright-routed HTTP/HTTPS requests such as redirects, iframe navigations, fetch/XHR, and subresources.

## Evidence Redaction Changes

- JSON and HTML evidence artifacts are centrally redacted before write.
- Screenshot capture is disabled by default for non-harness targets.
- Bundle manifests now record screenshot sensitivity metadata and explicitly state that pixel-level screenshot redaction is not implemented.

## APNTalk Support-Status Clarification

- APNTalk remains contract scaffold only.
- Unsupported APNTalk browser actions and runtime probes continue to fail closed.

## Schema and Lifecycle Tightening

- Timeout and free-text fields are bounded.
- Mutable defaults were removed from tool models.
- Broken-session behavior remains fail-closed for browser-dependent actions while diagnostic-safe paths remain available where intended.

## Live Transport Verification Outcome

- Real-host `stdio`, `streamable-http`, and `sse` smoke verification passed.
- Non-local HTTP/SSE fail-closed startup behavior and authenticated protected-path behavior were verified on a host-capable runtime.

## Residual Limitations

- Browser request governance is bounded to requests surfaced through Playwright routing.
- Screenshot pixel redaction is intentionally residual.
- Production still depends on operator-managed proxy/firewall/token rotation/outbound egress controls.
