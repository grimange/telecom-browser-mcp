# 13 README and Usage

## What Codex changed
- Rewrote `README.md` with:
  - architecture boundaries
  - install/run instructions
  - transport options
  - testing instructions
  - artifact layout
- Added developer guides:
  - `docs/guides/adapters.md`
  - `docs/guides/testing.md`
  - `docs/guides/host-setup.md`

## What Codex intentionally did not change
- Did not add screenshots or animated walkthroughs.

## Tests run
- `python -m pytest -q`

## Evidence produced
- Documentation updates and command paths validated in local environment.

## Open risks
- Host-specific onboarding examples may require additional tuning for non-FastMCP clients.

## Next recommended batch
- batch-10-hardening-followups.md
