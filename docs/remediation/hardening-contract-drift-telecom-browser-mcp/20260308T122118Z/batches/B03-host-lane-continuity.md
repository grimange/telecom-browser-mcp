# B03 Host Lane Continuity

- objective: reduce confidence gap from host-gated skips
- source findings: TC-002
- target files:
  - .github/workflows/ci.yml
- acceptance: host-e2e workflow job runs `-m host_required` and requires at least one pass
- status: closed
