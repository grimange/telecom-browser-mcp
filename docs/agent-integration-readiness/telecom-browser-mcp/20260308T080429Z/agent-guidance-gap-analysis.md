# Agent Guidance Gap Analysis

## Scope audited

- `AGENTS.md`
- `README.md`
- `docs/guides/host-setup.md`

## Required guidance checks

1. Explain what `telecom-browser-mcp` is for.
2. Explain host requirement for browser-driving tools.
3. Explain sandbox failures are not automatic code defects.
4. Explain when Codex should use MCP tools.

## Findings

- Item 1: `pass` (already present in AGENTS and README).
- Item 2: `was partial`, now `pass` after adding explicit Host Execution Policy in `AGENTS.md` and host-vs-sandbox section in `README.md`.
- Item 3: `pass` (Sandbox-Aware Guidance existed; now strengthened with explicit policy language).
- Item 4: `was partial`, now `pass` after adding `docs/usage/codex-agent-usage.md`.

## Gap closure actions completed in this run

- Added host execution policy subsection to `AGENTS.md`.
- Added Codex registration and host-vs-sandbox guidance to `README.md`.
- Added `docs/usage/codex-agent-usage.md`.
- Added `docs/setup/codex-mcp.md`.

## Residual guidance risks

- None blocking for integration readiness.
- Keep guidance synchronized if tool names or entrypoints change.
