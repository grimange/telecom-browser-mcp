# Next Run Instructions

Release hardening status: release_ready

## Allowed Pipelines
- closed_loop_validation_remediation: architecture pre-check satisfied
- closed_loop_stability_governor: closed-loop cycle available for stability evaluation
- architecture_guardrails_postcheck: post-remediation guardrail validation required
- cross_cycle_learning_engine: eligible by cycle cadence threshold (>=2 cycles)
- system_drift_detector: eligible by cadence/release policy
- remediate_live_verification_blockers: repair live verification blockers before release progression
- controlled_live_verification_recheck: re-run live verification after remediation
- pipeline_governor: re-evaluate global state after live verification refresh

## Blocked Pipelines
- expansionary_remediation: global verdict is blocked; limit scope until blocker cleared
- release_progression: live verification gate failed
