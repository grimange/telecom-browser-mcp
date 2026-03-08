from telecom_browser_mcp.system_drift_detector import DriftScoreEngine


def test_drift_score_low_is_architecture_stable() -> None:
    scorecard = DriftScoreEngine().score(
        dependency_drift={"dependency_edge_count": 10, "cross_layer_edge_count": 4, "reciprocal_dependency_pair_count": 0},
        boundary_violations=[],
        prior_scorecard=None,
    )
    assert scorecard["drift_outcome"] == "architecture_stable"


def test_drift_score_with_critical_violation_is_severe() -> None:
    scorecard = DriftScoreEngine().score(
        dependency_drift={
            "dependency_edge_count": 500,
            "cross_layer_edge_count": 200,
            "reciprocal_dependency_pair_count": 10,
        },
        boundary_violations=[{"severity": "critical"}],
        prior_scorecard=None,
    )
    assert scorecard["drift_severity"] == "severe"
