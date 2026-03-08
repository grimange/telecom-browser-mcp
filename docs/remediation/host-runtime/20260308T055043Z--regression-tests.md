# Regression Tests

Added/updated tests:
- `tests/live_verification/test_startup_timeout_classification.py`
  - startup requires handshake success for ready classification
- `tests/live_verification/test_handshake_probe.py`
  - initialize request contract
  - initialized/tools-list sequence contract
  - handshake classification mapping
- `tests/live_verification/test_browser_runtime_classification.py`
  - host sandbox constraint classification
- `tests/pipeline_governor/test_live_verification_override.py`
  - release-track override remains enforced when live verification is blocked

Execution:
- `9 passed`
