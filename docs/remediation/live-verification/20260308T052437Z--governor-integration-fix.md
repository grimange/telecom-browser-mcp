# Governor Integration Fix

Implemented in `src/telecom_browser_mcp/pipeline_governor.py`:
- Added live-verification artifact ingestion.
- Added global override:
  - if `live_verification_verdict == blocked` and base verdict is `release_candidate`, emit `blocked_by_live_verification`.
- Enforced release gating:
  - `release_track_allowed=false`
  - `release_block_reason` includes `live_verification_blocked`
- Added next actions:
  - `remediate_live_verification_blockers`
  - `controlled_live_verification_recheck`
  - re-run `pipeline_governor`

CLI integration:
- `scripts/run_pipeline_governor.py` accepts `--live-verification-dir`.

Regression coverage:
- `tests/pipeline_governor/test_live_verification_override.py`

Rerun outcome:
- governor now emits `global_verdict=blocked_by_live_verification`.
