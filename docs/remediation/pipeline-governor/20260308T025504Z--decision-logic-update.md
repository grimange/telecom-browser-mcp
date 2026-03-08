# Decision Logic Update

Release-track override was added in `PipelineGovernor.decide`.

Rules now enforced:

- baseline `release_candidate` + `release_hardening_verdict=release_blocked`
  -> `global_verdict=blocked_by_release_hardening`
- baseline `release_candidate` + `release_hardening_verdict in {release_hardening_incomplete, release_hardening_not_available}`
  -> `global_verdict=release_hardening_incomplete`
- baseline `release_candidate` + `release_hardening_verdict=release_ready`
  -> release progression allowed (remains `release_candidate`)

Additional outputs:

- `release_hardening_verdict`
- `release_track_allowed`
- `release_block_reason`
- `release_hardening_required`
