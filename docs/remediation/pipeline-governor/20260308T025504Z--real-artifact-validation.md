# Real Artifact Validation

Executed:

- `python scripts/run_pipeline_governor.py`

Observed with current release-hardening artifacts:

- `global_verdict=blocked_by_release_hardening`
- `state=release-blocked`
- `recommended_global_action=remediate_release_blockers`
- `release_hardening_verdict=release_blocked`
- `release_track_allowed=false`

Result:
The stale `release_candidate` outcome is revoked under release-hardening block as required.
