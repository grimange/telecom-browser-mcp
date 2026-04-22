#!/usr/bin/env bash
set -euo pipefail

mode="${1:-all}"

case "$mode" in
  stdio)
    tests=("tests/integration/test_transport_entrypoints.py" "tests/integration/test_stdio_smoke.py")
    ;;
  http)
    tests=("tests/integration/test_transport_entrypoints.py" "tests/integration/test_http_transport_smoke.py::test_streamable_http_first_contact_tools_live")
    ;;
  sse)
    tests=("tests/integration/test_transport_entrypoints.py" "tests/integration/test_http_transport_smoke.py::test_sse_first_contact_tools_live")
    ;;
  all)
    tests=(
      "tests/integration/test_transport_entrypoints.py"
      "tests/integration/test_stdio_smoke.py"
      "tests/integration/test_http_transport_smoke.py"
    )
    ;;
  *)
    echo "usage: bash scripts/run_live_transport_smoke.sh [stdio|http|sse|all]" >&2
    exit 2
    ;;
esac

MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1 .venv/bin/python -m pytest -q "${tests[@]}"
