# Instruction Output Update

`next-run-instructions.md` now includes explicit release-track status.

When release is blocked, output includes:

- `Release progression blocked by release hardening: <reasons>`
- required follow-up actions through planner outputs:
  - `release_hardening_remediation`
  - `release_hardening_recheck`
  - `pipeline_governor`
- blocked action:
  - `release_progression`
