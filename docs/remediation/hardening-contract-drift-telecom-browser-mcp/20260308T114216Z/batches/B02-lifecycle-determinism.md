# B02 Lifecycle Determinism

- objective: align runtime broken-session behavior with explicit lifecycle model transition
- source findings: BR-001
- severity: medium
- target files:
  - src/telecom_browser_mcp/tools/service.py
- root cause: broken session errors emitted without updating lifecycle state
- remediation steps:
  - set `runtime.model.lifecycle_state = "broken"` in broken-page gate
- acceptance checks:
  - static inspection confirms explicit transition before `session_broken` error return
- regression guards:
  - add lifecycle transition tests in future hardening suite
- rollback concerns:
  - none beyond state-model consumers relying on previous implicit behavior
