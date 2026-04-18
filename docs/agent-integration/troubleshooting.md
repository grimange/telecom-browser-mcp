# Troubleshooting

## Common Failure Classes
- `environment_limit_missing_browser_binary`: Browser-driving tools can degrade when Playwright browser binaries are unavailable.
- `environment_limit_unreachable_target`: open_app can fail/degrade when target URL is unreachable.
- `permission_blocked`: Sandbox/runtime restrictions can block browser launch or transport sockets.
- `adapter_target_mismatch`: Known APNTalk hosts reject explicit adapter overrides that would bypass the mapped adapter.
- `adapter_contract_unimplemented`: The resolved adapter advertises the tool surface but has no truthful implementation for that APNTalk path yet.
- `selector_contract_missing`: The APNTalk UI selector contract is not pinned, so readiness or action flows fail closed instead of reporting scaffold success.
- `runtime_probe_unavailable`: The APNTalk runtime probe path is not implemented or not discoverable for the requested operation.
- If browser-driving flows fail in sandboxed runtime, classify as environment limitation unless host runtime reproduces the defect.

## Fast Checks
1. Run `health`, `capabilities`, `list_sessions` first to verify server/tool discovery path.
2. If browser tools degrade, verify Playwright browser binaries on host runtime.
3. For HTTP transport, verify `FASTMCP_HOST` / `FASTMCP_PORT` and endpoint reachability.
4. Treat sandbox restrictions as environment limitations unless host runtime reproduces the same failure.
5. For APNTalk targets, do not override the adapter mapping with `generic`; a truthful mismatch error is expected.

## Verification Gaps
- Client-specific runtime transcripts are not captured by this documentation pipeline run.
