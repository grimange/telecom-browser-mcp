from pathlib import Path

from telecom_browser_mcp.architecture_guardrails import run_architecture_guardrails


def test_guardrails_writes_required_artifacts(tmp_path: Path) -> None:
    src_root = tmp_path / "src/telecom_browser_mcp"
    src_root.mkdir(parents=True)
    (src_root / "__init__.py").write_text("", encoding="utf-8")
    (src_root / "models.py").write_text("x=1\n", encoding="utf-8")

    closed_loop = tmp_path / "closed-loop"
    closed_loop.mkdir(parents=True)
    (closed_loop / "20260308T010203Z--batch-execution-results.json").write_text(
        '{"selected_batches": []}', encoding="utf-8"
    )

    out = tmp_path / "out"
    result = run_architecture_guardrails(
        src_root=src_root,
        closed_loop_dir=closed_loop,
        output_dir=out,
    )

    assert result["guardrails_verdict"] in {"guardrails_pass", "guardrails_warn", "guardrails_block"}
    for file_name in [
        "guardrail-violations.json",
        "dependency-rule-results.json",
        "boundary-rule-results.json",
        "guardrails-verdict.json",
        "guardrails-precheck.md",
        "guardrails-postcheck.md",
        "boundary-rule-results.md",
        "dependency-rule-results.md",
        "contract-layer-rule-results.md",
        "guardrails-verdict.md",
    ]:
        assert (out / file_name).exists()
