from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_baseline_corpus_has_expected_targets_and_scenarios() -> None:
    corpus_path = _repo_root() / "docs" / "modernization" / "baseline-corpus.json"
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

    entries = {entry["scenario_id"]: entry for entry in corpus["entries"]}
    assert "apntalk-modernization-baseline" in entries
    assert "fake-dialer-happy-path" in entries
    assert "connected_no_remote_audio" in entries["fake-dialer-happy-path"]["fixture_scenarios"]


def test_modernization_docs_exist() -> None:
    repo_root = _repo_root()
    assert (repo_root / "docs" / "modernization" / "apntalk-scenario-catalog.md").exists()
    assert (repo_root / "docs" / "modernization" / "apntalk-modernization-review.md").exists()
    assert (repo_root / "docs" / "remediation" / "apntalk-modernization-loop.md").exists()
