name: telecom-mcp-audit

description: Use when auditing a telecom_mcp repository or telecom automation code for MCP integration quality, contract drift, transport/startup issues, or production-readiness gaps. Produces persistent audit artifacts and remediation task batches. Do not use for direct feature implementation or uncontrolled live remediation.

## Use When
- auditing telecom_mcp integration
- verifying MCP server correctness
- reviewing production readiness
- evaluating drift between docs and implementation
- producing inspection artifacts before remediation

## Do Not Use When
- implementing new features
- fixing isolated bugs
- running destructive telecom actions
- writing general documentation
- generating release notes

## Scope
- Inspection-first behavior: findings before fixes.
- Persistent, timestamped artifacts under `docs/audit/telecom-mcp/<timestamp>/`.
- Evidence-backed conclusions only.

## Safety Rules
- Do not auto-remediate by default.
- Do not execute destructive telecom actions.
- Do not infer production facts without evidence.
- Do not overwrite prior audit artifacts.
- Treat sandbox/browser limitations as environment constraints unless code evidence proves defects.

## Outputs
- `audit-summary.md`
- `evidence-index.md`
- `mcp-integration-findings.md`
- `contract-drift-findings.md`
- `production-readiness-findings.md`
- `root-cause-and-risk-map.md`
- `remediation-batches.md`

## Candidate Revision Notes
- Generated from repeated evidence clusters; promotion remains manual.
- Generated at: 2026-03-08T10:42:15.109741+00:00
- Enforce explicit artifact checklist in completion steps.
- Tighten trigger and non-trigger routing boundaries.
- Require deterministic validation pass before final output.

