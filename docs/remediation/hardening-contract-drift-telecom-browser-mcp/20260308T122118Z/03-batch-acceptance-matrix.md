# 03 Batch Acceptance Matrix

| Batch | Acceptance check | Result |
|---|---|---|
| B01 | `SessionManager.mark_broken` exists and is used by tool guard | pass |
| B02 | redaction patterns include broader secret formats and tests pass | pass |
| B03 | CI defines host-e2e lane with `host_required` execution and pass guard | pass |
| All | static verification suite (`ruff`, unit/contract/bootstrap tests) | pass |
