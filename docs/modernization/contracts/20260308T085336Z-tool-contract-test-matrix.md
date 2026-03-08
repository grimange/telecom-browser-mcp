# Tool Contract Test Matrix

- timestamp: 2026-03-08T08:53:36Z

| Test ID | Check | Implementation | Status |
| --- | --- | --- | --- |
| T1 | Tool listing | `test_tool_listing_matches_catalog` | pass |
| T2 | Valid invocation | `test_valid_invocation_noarg_tool` | pass |
| T3 | Invalid invocation rejection | `test_invalid_envelope_rejected_for_noarg_tool` | pass |
| T4 | No-arg tool schema | `test_noarg_tools_publish_empty_object_schema` | pass |
| T5 | Strict schema properties | `test_all_tools_publish_strict_input_schema` | pass |
| T6 | Signature/schema parity | `test_signature_schema_parity_for_registered_tools` | pass |

## Verification Commands

- `PYTHONPATH=src .venv/bin/pytest -q tests/contracts/test_tool_contract_parity.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_tool_invocation_compatibility.py tests/e2e/test_stdio_smoke.py`

## Inventory Artifact

- `docs/modernization/contracts/20260308T085336Z-tool-contract-inventory.json`
