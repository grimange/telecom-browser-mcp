from telecom_browser_mcp.failure_priority_scorer import classify_domain


def test_environment_vs_product_split() -> None:
    product = {"category": "selector_stale_after_dom_refresh"}
    env = {"category": "environment_blocked_execution"}
    gap = {"category": "diagnostics_bundle_missing_on_failure"}
    assert classify_domain(product) == "product_logic"
    assert classify_domain(env) == "environment_or_ci"
    assert classify_domain(gap) == "diagnostics_pipeline"
