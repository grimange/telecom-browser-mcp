from telecom_browser_mcp.architecture_guardrails import BoundaryRuleEvaluator, ImportEdge


def test_boundary_flags_non_adapter_import_of_concrete_adapter() -> None:
    edges = [
        ImportEdge(
            src_module="telecom_browser_mcp.tools.orchestrator",
            src_layer="tools",
            dst_module="telecom_browser_mcp.adapters.apntalk",
            dst_layer="adapters",
        )
    ]
    result = BoundaryRuleEvaluator().evaluate(edges=edges)
    assert result["violation_count"] == 1
    assert result["violations"][0]["rule_id"] == "BOUNDARY-ADAPTER-ISOLATION-001"
