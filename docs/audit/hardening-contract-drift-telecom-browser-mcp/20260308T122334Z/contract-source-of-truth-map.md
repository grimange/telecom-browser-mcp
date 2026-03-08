# Contract Source Of Truth Map

1. Canonical models: `CANONICAL_TOOL_INPUT_MODELS` + `ToolResponse`
2. Schema generation: `generate_all_tool_schemas`
3. Published schemas: `docs/contracts/m1/*.schema.json`
4. Runtime validators: `ToolService` Pydantic model validation
5. Parity tests: contract test suite
6. Docs: README/pipeline docs

No source-order conflicts detected.
