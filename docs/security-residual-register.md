# Security Residual Register

## Fully Closed

- Non-local HTTP/SSE startup exposure: fail-closed unless `TELECOM_BROWSER_MCP_UNSAFE_BIND=1` and `TELECOM_BROWSER_MCP_AUTH_TOKEN` are set.
- Initial `open_app` target validation: unsafe schemes, non-allowlisted hosts, unsafe DNS results, private/local/link-local/reserved/multicast/metadata targets are blocked before navigation.
- Textual evidence redaction: JSON/HTML artifacts pass through central redaction before write.

## Partially Closed

- Secondary browser request egress: Playwright-routed HTTP/HTTPS requests are governed with the same URL policy for document navigations, redirects, iframe navigations, fetch/XHR, and subresources. Remaining residual: browser-internal requests or protocol behavior not exposed through Playwright routing are not claimed as governed. Safeguard: deployment-layer egress controls remain required.

## Environment Blocked

- Live stdio/SSE/HTTP verification in constrained sandboxes: socket creation and/or subprocess first contact can be restricted by the runtime. Safeguard: live tests remain in the repo and CI, and host-capable verification requires:

```bash
MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 pytest -q \
  tests/integration/test_transport_entrypoints.py \
  tests/integration/test_stdio_smoke.py \
  tests/integration/test_http_transport_smoke.py
```

## Intentionally Residual

- Screenshot pixel redaction: not implemented and not claimed. Safeguards: screenshots are disabled by default for non-harness targets, omitted screenshots include reason text, manifests mark screenshots as sensitive, and operators are instructed not to commit real debug bundles.
