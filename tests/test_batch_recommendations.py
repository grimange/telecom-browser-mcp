from telecom_browser_mcp.remediation_batch_recommender import recommend_batches


def test_batch_recommendations_group_by_bucket_and_domain() -> None:
    ranked = [
        {
            "signature_id": "SIG-001",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "contract_ids": ["LIFECYCLE::stale_selector_recovery"],
            "occurrence_count": 2,
        },
        {
            "signature_id": "SIG-002",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "contract_ids": ["LIFECYCLE::crash_recovery"],
            "occurrence_count": 1,
        },
        {
            "signature_id": "SIG-010",
            "priority_bucket": "P4",
            "domain": "environment_or_ci",
            "contract_ids": ["PROTOCOL::initialize_and_discovery"],
            "occurrence_count": 1,
        },
    ]
    batches = recommend_batches(ranked)
    assert batches
    first = batches[0]
    assert first["priority_bucket"] == "P0"
    assert first["domain"] == "product_logic"
    assert set(first["target_signature_ids"]) == {"SIG-001", "SIG-002"}


def test_batch_recommendations_skip_zero_occurrence_templates() -> None:
    ranked = [
        {
            "signature_id": "SIG-000",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "contract_ids": [],
            "occurrence_count": 0,
        },
        {
            "signature_id": "SIG-001",
            "priority_bucket": "P1",
            "domain": "product_logic",
            "contract_ids": ["LIFECYCLE::stale_selector_recovery"],
            "occurrence_count": 2,
        },
    ]
    batches = recommend_batches(ranked)
    assert len(batches) == 1
    assert batches[0]["target_signature_ids"] == ["SIG-001"]
