# Environment Noise Quarantine

- risk_id: RISK-ENV-001
- severity: high
- source_cycle: 20260307T234505Z
- blocker: interop probe timed out at artifact timestamp 20260307T123030Z
- quarantine_goal: isolate environment instability from product remediation decisions

## Quarantine Rules

- Keep remediation scope at `max_batches=1`.
- Do not increase remediation scope until environment gate is cleared.
- Treat interop timeout outcomes as `environment blocked`, not product regressions.

## Environment Gate (Exit Criteria)

- Interop probe passes in 2 consecutive runs.
- No new environment blockers added in latest closed-loop `improvement-delta.json`.
- Governor high-risk count for `RISK-ENV-001` drops to 0.

## Monitoring Checklist

- Run `scripts/run_mcp_interop_probe.py` and record artifact path + status.
- Rerun closed-loop cycle in reduced scope and stability governor.
- Confirm `enforcement_action` remains constrained until exit criteria are met.
