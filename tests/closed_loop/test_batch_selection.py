from telecom_browser_mcp.closed_loop import BatchSelectionCoordinator


def test_batch_selection_prefers_high_priority_non_environment_batches() -> None:
    recommended_batches = [
        {
            "batch_id": "RB-001",
            "priority_bucket": "P0",
            "domain": "product_logic",
            "target_signature_ids": ["SIG-001"],
        },
        {
            "batch_id": "RB-002",
            "priority_bucket": "P1",
            "domain": "diagnostics_pipeline",
            "target_signature_ids": ["SIG-002"],
        },
        {
            "batch_id": "RB-003",
            "priority_bucket": "P1",
            "domain": "environment_or_ci",
            "target_signature_ids": ["SIG-003"],
        },
    ]
    ranked_signatures = [
        {"signature_id": "SIG-001", "score": 80},
        {"signature_id": "SIG-002", "score": 65},
        {"signature_id": "SIG-003", "score": 62},
    ]

    output = BatchSelectionCoordinator().select(
        recommended_batches=recommended_batches,
        ranked_signatures=ranked_signatures,
        max_batches=2,
    )

    selected_ids = [item["batch_id"] for item in output["selected_batches"]]
    assert selected_ids == ["RB-001", "RB-002"]
