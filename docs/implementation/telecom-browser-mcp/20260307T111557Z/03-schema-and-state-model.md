# 03 Schema and State Model

## What Codex changed
- Added strict models in `models/`:
  - `ArtifactRef`, `BrowserSessionModel`, `RegistrationSnapshot`, `CallSnapshot`, `WebRtcSnapshot`, `DiagnosticResult`
- Added shared enums:
  - browser session state, registration state, call state, webrtc state, error/failure enums
- Added standard response/failure envelopes in `models/envelope.py`.
- Added unit tests for schema and envelope shape.

## What Codex intentionally did not change
- Did not introduce versioned schema migration paths yet.

## Tests run
- `python -m pytest -q tests/unit/test_models.py`

## Evidence produced
- Model serialization and envelope contract assertions in unit tests.

## Open risks
- Some diagnostic severity/confidence fields are static defaults and need future tuning.

## Next recommended batch
- batch-04-registration.md
