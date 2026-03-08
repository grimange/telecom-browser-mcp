# Tool Parity Test Plan (Static)

- Timestamp: `20260308T094744Z`

## Test Matrix

| ID | Goal | Test/Check | Location |
|---|---|---|---|
| T1 | Tool registration inventory | `test_tool_listing_matches_catalog` | `tests/contracts/test_tool_contract_parity.py` |
| T2 | Public signature vs wrapper signature parity | `test_signature_schema_parity_for_registered_tools` | `tests/contracts/test_tool_contract_parity.py` |
| T3 | Wrapper signature vs runtime signature parity | `test_registration_uses_direct_bound_handlers_without_kwargs_wrappers` + static binding checks | `tests/contracts/test_tool_contract_parity.py`, `tests/contracts/test_registration_pattern_static.py` |
| T4 | No-arg strictness / no synthetic `kwargs` | `test_invalid_envelope_rejected_for_noarg_tool`, `test_noarg_tools_publish_empty_object_schema`, `test_no_tool_publishes_synthetic_kwargs_field`, `test_dispatch_does_not_forward_nested_kwargs_key` | `tests/contracts/test_tool_contract_parity.py`, `tests/unit/test_tool_invocation_compatibility.py` |
| T5 | Canonical registration pattern conformance | `test_canonical_registration_site_is_unique`, `test_register_function_binds_direct_handler`, `test_register_function_has_no_nested_kwargs_wrapper` | `tests/contracts/test_registration_pattern_static.py` |

## CI Commands

```bash
pytest -q tests/contracts/test_tool_contract_parity.py
pytest -q tests/contracts/test_registration_pattern_static.py
pytest -q tests/unit/test_tool_invocation_compatibility.py
bash scripts/check_static_contract_guardrails.sh
```

## Expected Failure Signals

- inventory mismatch: missing/extraneous tool registration
- signature/schema mismatch: drift between public schema and runtime signature
- synthetic `kwargs` leakage: no-arg tools publish/accept envelope unexpectedly
- registration-pattern drift: non-canonical or wrapper-based registration reintroduced
