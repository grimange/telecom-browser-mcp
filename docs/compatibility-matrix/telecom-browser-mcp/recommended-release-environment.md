# Recommended Release Environment

- project: `telecom-browser-mcp`
- policy_version: `2026-03-08.v1`
- objective: run `016--controlled-live-verification` in an authoritative runtime

## Required Runtime Class

- `authoritative_host` (preferred)
- `container_runtime` (allowed only when browser capability is verified)

## Explicitly Rejected for Release Gate

- `sandbox_runtime`
- `restricted_runtime`
- `unknown_environment`
- `wsl_runtime`

## Transport + Browser Mode

- transport: `stdio`
- browser execution mode: `playwright_headless_chromium`

## Host Prerequisites

- Python virtual environment installed (`.venv`)
- Playwright browser binaries present on host
- ability to spawn subprocesses and Chromium
- no sandbox policy that blocks Chromium launch
