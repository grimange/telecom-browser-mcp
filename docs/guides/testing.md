# Testing Guide

## Run tests

```bash
python -m pytest -q
```

## Test tiers

- `tests/unit`: imports, models, adapter registry shape
- `tests/integration`: harness-backed flow and diagnostics
- `tests/e2e`: stdio quickstart smoke through orchestration

## Environment-sensitive behavior

Playwright/browser binary requirements are environment-sensitive. Current tests use the harness adapter and do not require browser launch.

## Lint

```bash
python -m ruff check src tests
```
