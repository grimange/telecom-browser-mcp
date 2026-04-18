# telecom-browser-mcp — Codex Repository Guidance

## Mission
This repository is a telecom-aware browser MCP server and test harness. Optimize for:
1. truthful MCP/tool contracts
2. fail-closed adapter behavior
3. deterministic evidence collection
4. harness-first reproduction
5. runtime-realistic verification before claiming product regressions

## Read first
Before editing, read the minimum relevant truth:
- `README.md`
- `docs/setup/codex-mcp.md`
- `docs/usage/codex-agent-usage.md`
- `.github/workflows/tool-contracts.yml`
- the touched code path under `src/telecom_browser_mcp/**`
- the closest matching tests under `tests/**`

Read more only when needed to complete the task truthfully.

## Contract authority order
When sources disagree, prefer repository truth in this order:
1. `.github/workflows/tool-contracts.yml`
2. contract and integration tests that exercise the public MCP surface
3. runtime code under `src/telecom_browser_mcp/**`
4. setup and usage docs under `docs/**`
5. `README.md`

Do not loosen tests or workflow expectations to fit accidental behavior unless the contract change is intentional, implemented, verified, and documented.

When docs disagree with executable truth, update docs in the same task.

## Repo rules that apply every time
- Keep public MCP inputs explicit. Do not publish a public top-level `kwargs` field.
- Preserve structured response envelopes and explicit failure metadata.
- Prefer repo scripts, MCP tools, harness flows, and adapter hooks over generic click/select hacks.
- For APNTalk adapter paths, fail closed when behavior is not implemented. Do not let generic scaffold defaults, inherited stubs, or placeholder success envelopes masquerade as working behavior.
- Treat sandbox-only browser launch, device, signaling, or media limitations as environment findings unless reproduced in a host-capable runtime.
- Collect evidence before remediation when the task is runtime-, browser-, signaling-, or media-related.
- Changes are not done until relevant tests and docs are updated in the same task.
- Do not silently change public MCP tool names, required fields, response envelopes, or failure semantics.
- Prefer the smallest defensible change that preserves contract clarity and reproducibility.
- Do not convert an environment limitation into a product bug claim without reproduction evidence.

## Preferred execution order
1. Map the real execution path.
2. Identify the smallest defensible slice.
3. Reproduce and collect evidence when the issue is runtime-facing.
4. Implement.
5. Run narrow verification first.
6. Run broader verification as needed.
7. Update docs and evidence.
8. Summarize residual risk and any remaining environment constraints.

## Verification minimums
- MCP tool input/output/envelope changes:
  run the exact contract workflow commands from `.github/workflows/tool-contracts.yml` and the closest contract tests.
- Adapter behavior changes:
  run the closest unit tests and the narrowest harness or integration path that exercises the adapter.
- Runtime, browser, media, or signaling changes:
  reproduce with harness evidence first, classify environment vs product, then run host-capable verification before claiming a product regression.
- Diagnostics or evidence pipeline changes:
  verify deterministic artifact shape, failure metadata, and nearest affected tests.
- Docs-only changes:
  verify referenced commands, paths, filenames, and tool names still exist.

Broaden verification only after the narrow slice passes or when the task changes a shared contract surface.

## Evidence and artifact handling
- Save deterministic evidence for runtime-facing issues whenever practical.
- Prefer structured artifacts over prose-only claims.
- Redact secrets, tokens, credentials, phone numbers, session identifiers, and private endpoints before committing artifacts or docs.
- Do not claim live-service regressions from unsaved, non-reproducible, or sandbox-only observations.
- When evidence is incomplete, say so explicitly and keep the conclusion bounded.

## Preferred tools and commands
- Search: `rg`, `rg --files`
- Bootstrap: `python -m pip install -e .[dev]`
- Browser deps: `python -m playwright install chromium`
- MCP smoke (if available): `health`, `capabilities`, `list_sessions`
- Interop probe: `python scripts/run_mcp_interop_probe.py`
- Follow the exact workflow commands in `.github/workflows/tool-contracts.yml` when MCP contract surfaces change.

## Directory map
- `src/telecom_browser_mcp/` — runtime code, adapters, tools, server, diagnostics, evidence
- `tests/` — unit, contract, integration, harness, live verification
- `scripts/` — bootstrap, probes, guardrails, release helpers
- `docs/setup/` — setup and registration
- `docs/usage/` — runtime guidance and operator flow
- `docs/` — diagnostics, release-hardening, remediation, governance-like process docs

## When to use subagents
- Use `repo_mapper` for large or cross-cutting tasks.
- Use `contract_reviewer` before or after changing MCP surfaces.
- Use `runtime_triager` for runtime/browser failures or live verification.
- Use `adapter_worker` for targeted adapter or tool implementation once the issue is understood.
- Use `ci_release_guard` for workflow, packaging, installability, and release-hardening tasks.
- Use `docs_evidence_curator` after evidence-heavy work.

If a named subagent is unavailable in the current runtime, continue without it. Do not invent missing subagents or pretend they ran.

## When to use skills
- `$telecom-mcp-bootstrap` for setup, registration, and first-run validation
- `$telecom-runtime-triage` for browser/runtime/environment splits
- `$adapter-contract-work` for adapter and APNTalk behavior changes
- `$tool-contract-guardrails` for MCP tool, schema, or envelope changes
- `$harness-scenario-work` for deterministic scenario packs
- `$diagnostics-evidence` for bundle review and failure classification
- `$release-hardening` for packaging, workflows, and docs alignment
- `$closed-loop-remediation` for multi-step reproduce → classify → repair → verify loops

If a named skill is unavailable in the current runtime, continue without it. Do not invent missing skills or block on them.

## Completion standard
A task is complete only when all of the following are true:
- the change is implemented
- the nearest relevant verification passes
- broader verification was run when required by the changed surface
- docs and operator guidance are aligned with the new truth
- residual risk, environment limits, and unverified assumptions are explicitly stated
