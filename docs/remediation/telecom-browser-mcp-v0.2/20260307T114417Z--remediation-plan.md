# Remediation Plan (20260307T114417Z)

## Input baseline
- Validation set: `docs/validation/telecom-browser-mcp-v0.2/20260307T113620Z--*`

## Planned execution order
1. Batch A protocol/schema normalization
2. Batch B browser lifecycle stabilization
3. Batch C telecom-flow corrections
4. Batch D diagnostics/bundle improvements
5. Batch E interop hardening
6. Contract clarifications

## Remediation strategy
- Fix confirmed contract FAIL items first (missing tool contracts).
- Keep environment/harness-gated scenarios as deferred unless lightweight safe fix exists.
- Preserve evidence and rerun targeted validations after each implemented batch.
