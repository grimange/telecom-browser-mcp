# Operator Migration Notes

## New or Tightened Environment Variables

- `TELECOM_BROWSER_MCP_UNSAFE_BIND`
- `TELECOM_BROWSER_MCP_AUTH_TOKEN`
- `TELECOM_BROWSER_MCP_ALLOWED_HOSTS`
- `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS`
- `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS`

## Default-Safe Behavior Changes

- HTTP/SSE default to localhost and fail closed on non-local bind without explicit opt-in and auth.
- `open_app` rejects unsafe schemes, non-allowlisted hosts, and local/private/link-local/reserved/multicast/metadata destinations.
- Routed browser HTTP/HTTPS requests surfaced by Playwright are checked against the same policy.
- Non-harness screenshots are disabled by default.

## Non-Local Deployment Requirements

- Set `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` only when remote exposure is intentional.
- Set `TELECOM_BROWSER_MCP_AUTH_TOKEN` for any non-local HTTP/SSE deployment.
- Keep reverse proxy, firewall, and outbound egress controls in place; repo controls are not a complete network perimeter.
- Rotate the bearer token through your existing secret-management and deployment path.

## Screenshot Handling Expectations

- Screenshots are sensitive artifacts.
- Pixel-level screenshot redaction does not exist.
- Prefer harness screenshots over real-target screenshots when possible.
- Enable `TELECOM_BROWSER_MCP_CAPTURE_SCREENSHOTS=1` only when secure handling is in place.

## Allowed-Host / Local-Target Expectations

- Use `TELECOM_BROWSER_MCP_ALLOWED_HOSTS` for real target allowlists.
- Use `TELECOM_BROWSER_MCP_ALLOW_LOCAL_TARGETS=1` only with an explicit local allowlist and only for harness/local-target testing.
- Do not carry harness-local settings into real-target production operation.
