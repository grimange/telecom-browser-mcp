# 04 Regression Guard Plan

- Guard RG-01: canonical tool map (`CANONICAL_TOOL_INPUT_MODELS`) is single source for schema generation and capability declaration.
- Guard RG-02: parity tests validate undeclared field rejection for all canonical tools.
- Guard RG-03: schema generation outputs are versioned artifacts and drift-checked in CI.
- Guard RG-04: unit tests enforce redaction behavior for known secret-like patterns.
- Guard RG-05: integration skip policy allows environment skips only for known constrained runtime classes.
