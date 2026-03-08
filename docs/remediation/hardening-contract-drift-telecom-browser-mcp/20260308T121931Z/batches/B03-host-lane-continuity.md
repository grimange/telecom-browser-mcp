# B03 Host Lane Continuity

- objective: reduce confidence gap from host-gated skips in constrained lanes
- source findings: TC-002
- severity: informational
- target files:
  - .github/workflows/ci.yml
- root cause: no dedicated host-capable lane for `host_required` tests
- remediation:
  - add `host-e2e` job
  - install playwright chromium
  - run `pytest -m host_required` and require at least one passed test
- acceptance: workflow defines host-e2e job with pass-presence guard
- regression guard: CI fails if host lane has zero passing host-required tests
