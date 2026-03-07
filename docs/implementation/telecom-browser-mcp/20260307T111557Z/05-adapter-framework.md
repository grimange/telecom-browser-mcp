# 05 Adapter Framework

## What Codex changed
- Added base adapter protocol: `adapters/base.py`.
- Added adapter registry: `adapters/registry.py`.
- Added scaffold adapters:
  - `apntalk`
  - `generic_sipjs`
  - `generic_jssip`
- Added deterministic harness adapter for integration testing.
- Added adapter developer guide at `docs/guides/adapters.md`.

## What Codex intentionally did not change
- Did not implement APNTalk production selectors/runtime hooks yet.

## Tests run
- `python -m pytest -q tests/unit/test_adapter_registry.py`

## Evidence produced
- Adapter registry test validation and harness tool-flow validation.

## Open risks
- Generic/APNTalk adapters return scaffold placeholders until selector/runtime contracts are filled.

## Next recommended batch
- batch-04-registration.md
