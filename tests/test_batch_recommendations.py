from telecom_browser_mcp.remediation_batch_recommender import recommend_batches


def test_batch_recommendations_group_by_bucket_and_domain() -> None:
    ranked = [
        {
            "signature_id": "SIG-001",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "contract_ids": ["LIFECYCLE::stale_selector_recovery"],
        },
        {
            "signature_id": "SIG-002",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "contract_ids": ["LIFECYCLE::crash_recovery"],
        },
        {
            "signature_id": "SIG-010",
            "priority_bucket": "P4",
            "domain": "environment_or_ci",
            "contract_ids": ["PROTOCOL::initialize_and_discovery"],
        },
    ]
    batches = recommend_batches(ranked)
    assert batches
    first = batches[0]
    assert first["priority_bucket"] == "P0"
    assert first["domain"] == "product_logic"
    assert set(first["target_signature_ids"]) == {"SIG-001", "SIG-002"}
