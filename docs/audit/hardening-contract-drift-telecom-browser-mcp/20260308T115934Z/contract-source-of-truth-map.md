# Contract Source Of Truth Map

1. Canonical input map: `src/telecom_browser_mcp/contracts/m1_contracts.py::CANONICAL_TOOL_INPUT_MODELS`
2. Schema export generator: `scripts/generate_contract_schemas.py`
3. Published schemas: `docs/contracts/m1/*.schema.json`
4. Runtime validation: model validators in `ToolService`
5. Tests: parity and envelope contract suites
6. Documentation: README/pipelines

Current ordering is aligned (no lower-layer contradiction observed).
