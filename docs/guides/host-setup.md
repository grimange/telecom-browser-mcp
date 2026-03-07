# Host Setup Examples

## Local stdio host

Use script command:

```bash
telecom-browser-mcp-stdio
```

## Streamable HTTP host

```bash
TELECOM_BROWSER_MCP_TRANSPORT=streamable-http telecom-browser-mcp-http
```

## SSE compatibility host

```bash
TELECOM_BROWSER_MCP_TRANSPORT=sse telecom-browser-mcp-sse
```

## Notes

- stdio is required/default path
- streamable-http is preferred remote standard path
- SSE is compatibility fallback for hosts that still require it

## Interop probe

Run lightweight discovery stability probe:

```bash
python scripts/run_mcp_interop_probe.py
```

This writes a JSON artifact under `docs/validation/telecom-browser-mcp-v0.2/artifacts/<timestamp>/logs/`.
