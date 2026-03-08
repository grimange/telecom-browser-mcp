# Full MCP Tool Contract Audit

- timestamp: 2026-03-08T08:53:36Z
- audited tools: 27
- inventory artifact: `docs/modernization/contracts/20260308T085336Z-tool-contract-inventory.json`

## Mismatch Class Definitions Applied

- C1 Synthetic Envelope Drift
- C2 Required Field Drift
- C3 Missing Schema Field
- C4 Naming Drift
- C5 Type Drift
- C6 Extra Properties Drift
- C7 Wrapper Mutation Drift

## High-Severity Findings

| Tool | Drift Type | Severity | Evidence | Fix |
| --- | --- | --- | --- | --- |
| list_sessions | C1, C7 | P0 | prior host failure: unexpected keyword argument `kwargs` | removed synthetic wrapper registration; bound tool directly to orchestrator handler |
| all no-arg tools | C6 | P1 | permissive argument model accepted unknown fields | forced strict arg model config (`extra=forbid`) so unknown fields are rejected |

## Full Surface Result (Post-Repair)

- C1-C5: none detected across 27 tools.
- C6: resolved; all published schemas now include `additionalProperties: false`.
- C7: resolved; canonical registration no longer relies on synthetic `**kwargs` wrappers.

## Current Audit Verdict

- P0 open issues: 0
- P1 open issues: 0
- contract status: pass
