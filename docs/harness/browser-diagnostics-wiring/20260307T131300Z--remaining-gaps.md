# Remaining Gaps (20260307T131300Z)

1. Live Playwright in lifecycle fault scenarios
- Current lifecycle scenarios are synthetic and do not execute live page/context objects.
- Result: bundles are structurally complete but often partial for screenshot/DOM/trace in harness-only sessions.

2. Trace configurability
- Trace capture is currently enabled at driver attach time and not yet controlled by settings flags.

3. Request/response depth
- Network artifacts currently capture summaries only.
- No body/header redaction policy is applied yet for richer payload capture.

4. Pipeline coupling
- Diagnostics wiring artifacts are generated and tested, but existing v0.2 validation summary docs are not auto-updated by this pipeline yet.
