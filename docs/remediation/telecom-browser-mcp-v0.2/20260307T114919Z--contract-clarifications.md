# Contract Clarifications

1. Full wire-level protocol validation:
- Clarify whether lightweight deterministic discovery probe is acceptable for remediation PASS,
  or whether MCP Inspector trace artifacts are mandatory in all environments.

2. Screenshot requirement semantics:
- Current behavior returns a deterministic placeholder screenshot when browser page is unavailable.
- Clarify whether this is acceptable as contract-satisfying fallback for non-browser harness runs.
