# 10 - Residual Risk Ledger

| Risk ID | Severity | Risk | Why It Remains | Recommended Action |
|---|---|---|---|---|
| R-1001 | P1 | Runtime transport proof still environment-dependent | strict mode added, but this environment cannot provide passing host runtime evidence | execute strict smoke in host lane with socket/stdio permissions and archive artifacts |
| R-1002 | P2 | Diagnostics taxonomy remains mixed | out of scope for this targeted pass | run dedicated diagnostics normalization pipeline with compatibility mapping |
