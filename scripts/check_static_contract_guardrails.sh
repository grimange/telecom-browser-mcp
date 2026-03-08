#!/usr/bin/env bash
set -euo pipefail

fail=0

echo "[guardrail] Verify canonical tool registration site"
registration_hits="$(rg -n 'server\.tool\(' src/telecom_browser_mcp/server || true)"
registration_count="$(printf '%s\n' "${registration_hits}" | sed '/^$/d' | wc -l | tr -d ' ')"
if [[ "${registration_count}" != "1" ]]; then
  echo "[guardrail][FAIL] Expected exactly one server.tool(...) site in server layer; found ${registration_count}"
  printf '%s\n' "${registration_hits}"
  fail=1
fi
if ! rg -n 'server\.tool\(name=tool_name\)\(handler\)' src/telecom_browser_mcp/server/stdio_server.py >/dev/null; then
  echo "[guardrail][FAIL] Missing canonical direct registration call in stdio_server.py"
  fail=1
fi

echo "[guardrail] Reject synthetic **kwargs wrapper defs in transport registration modules"
if rg -n '^\s*(async\s+def|def)\s+[A-Za-z_][A-Za-z0-9_]*\([^)]*\*\*kwargs' \
  src/telecom_browser_mcp/server/stdio_server.py \
  src/telecom_browser_mcp/server/sse_server.py \
  src/telecom_browser_mcp/server/streamable_http_server.py; then
  echo "[guardrail][FAIL] Found disallowed **kwargs wrapper function in server transport path"
  fail=1
fi

echo "[guardrail] Restrict legacy kwargs-envelope keys to internal dispatch helper only"
envelope_hits="$(rg -n '"kwargs"|payload\.get\("kwargs"\)|payload\["kwargs"\]' src/telecom_browser_mcp || true)"
disallowed_envelope_hits="$(printf '%s\n' "${envelope_hits}" | rg -v '^src/telecom_browser_mcp/server/app.py:' || true)"
if [[ -n "${disallowed_envelope_hits}" ]]; then
  echo "[guardrail][FAIL] Found disallowed kwargs-envelope usage outside server/app.py"
  printf '%s\n' "${disallowed_envelope_hits}"
  fail=1
fi

echo "[guardrail] Reject direct forwarding of raw payload/kwargs maps to handlers"
if rg -n 'handler\(\*\*(payload|kwargs)\)' src/telecom_browser_mcp; then
  echo "[guardrail][FAIL] Found raw payload forwarding into handler(**...)"
  fail=1
fi

if [[ "${fail}" != "0" ]]; then
  echo "[guardrail] static contract guardrails: FAIL"
  exit 1
fi

echo "[guardrail] static contract guardrails: PASS"
