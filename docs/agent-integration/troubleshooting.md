# Troubleshooting

## Common Failure Classes
- `environment_limit_missing_browser_binary`: Browser-driving tools can degrade when Playwright browser binaries are unavailable.
- `environment_limit_unreachable_target`: open_app can fail/degrade when target URL is unreachable.
- `permission_blocked`: Sandbox/runtime restrictions can block browser launch or transport sockets.
- If browser-driving flows fail in sandboxed runtime, classify as environment limitation unless host runtime reproduces the defect.

## Fast Checks
1. Run `health`, `capabilities`, `list_sessions` first to verify server/tool discovery path.
2. If browser tools degrade, verify Playwright browser binaries on host runtime.
3. For HTTP transport, verify `FASTMCP_HOST` / `FASTMCP_PORT` and endpoint reachability.
4. Treat sandbox restrictions as environment limitations unless host runtime reproduces the same failure.

## Verification Gaps
- Client-specific runtime transcripts are not captured by this documentation pipeline run.
