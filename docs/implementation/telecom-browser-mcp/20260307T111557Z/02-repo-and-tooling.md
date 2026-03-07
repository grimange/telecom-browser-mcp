# 02 Repo and Tooling

## What Codex changed
- Added `pyproject.toml` with package metadata, dependencies, scripts, pytest/ruff config.
- Added `.env.example`.
- Added setup scripts:
  - `scripts/bootstrap.sh`
  - `scripts/install_playwright_browsers.sh`
- Created package and test directory skeletons.

## What Codex intentionally did not change
- Did not pin transitive dependencies.
- Did not add CI workflow in this batch.

## Tests run
- `python -m ruff check --fix src tests`
- `python -m pytest -q` (8 passed)

## Evidence produced
- Package install + lint/test command outputs from local run.

## Open risks
- Browser binaries may be unavailable in restricted environments unless explicitly installed.

## Next recommended batch
- batch-02-session-lifecycle.md
