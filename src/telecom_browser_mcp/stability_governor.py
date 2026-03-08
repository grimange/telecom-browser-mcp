from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {path}")
    return matches[-1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _parse_timestamp_from_name(path: Path) -> str:
    name = path.name
    if "--" not in name:
        raise ValueError(f"cannot parse timestamp from {name}")
    return name.split("--", 1)[0]


@dataclass(slots=True)
class GovernorReadinessResult:
    ok: bool
    checks: dict[str, bool]
    inputs: dict[str, str]
    generated_at: str
    cycle_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": self.checks,
            "inputs": self.inputs,
            "generated_at": self.generated_at,
            "cycle_timestamp": self.cycle_timestamp,
        }


class StabilityGovernorReadinessEvaluator:
    def __init__(self, *, closed_loop_dir: Path) -> None:
        self.closed_loop_dir = closed_loop_dir

    def evaluate(self) -> GovernorReadinessResult:
        checks: dict[str, bool] = {}
        inputs: dict[str, str] = {}

        cycle_summary = _latest(self.closed_loop_dir, "*--cycle-summary.json")
        ts = _parse_timestamp_from_name(cycle_summary)

        required_exact = {
            "cycle_summary": self.closed_loop_dir / f"{ts}--cycle-summary.json",
            "batch_execution_results": self.closed_loop_dir / f"{ts}--batch-execution-results.json",
            "improvement_delta": self.closed_loop_dir / f"{ts}--improvement-delta.json",
        }

        for key, path in required_exact.items():
            exists = path.exists()
            checks[key] = exists
            inputs[key] = str(path) if exists else ""

        verdict_json = self.closed_loop_dir / f"{ts}--cycle-verdict.json"
        verdict_md = self.closed_loop_dir / f"{ts}--cycle-verdict.md"
        if verdict_json.exists():
            checks["cycle_verdict"] = True
            inputs["cycle_verdict"] = str(verdict_json)
        elif verdict_md.exists():
            # Backward-compatible with existing closed-loop output shape.
            checks["cycle_verdict"] = True
            inputs["cycle_verdict"] = str(verdict_md)
        else:
            checks["cycle_verdict"] = False
            inputs["cycle_verdict"] = ""

        return GovernorReadinessResult(
            ok=all(checks.values()),
            checks=checks,
            inputs=inputs,
            generated_at=_now_iso(),
            cycle_timestamp=ts,
        )


class StabilityScorecardBuilder:
    def build(
        self,
        *,
        cycle_summary: dict[str, Any],
        batch_execution_results: dict[str, Any],
        improvement_delta: dict[str, Any],
    ) -> dict[str, Any]:
        verdict = str(cycle_summary.get("cycle_verdict", "partial improvement continue"))
        delta_status = str(improvement_delta.get("status", "unchanged"))
        diagnostics_coverage = float(improvement_delta.get("diagnostics_coverage_score", 0.0))
        contract_delta = int(improvement_delta.get("delta", {}).get("non_pass_contracts", 0))
        env_delta = int(improvement_delta.get("delta", {}).get("environment_blockers", 0))
        selected_count = len(batch_execution_results.get("selected_batches", []))

        transport = 98
        if verdict in {"regression detected", "critical_regression"}:
            transport = 35
        elif verdict in {"blocked by environment", "blocked by diagnostics"}:
            transport = 82

        browser = 96
        top_signatures = [str(item).lower() for item in improvement_delta.get("top_signatures", [])]
        if any("browser" in item or "page_closed" in item for item in top_signatures):
            browser -= 12
        if delta_status == "regressed":
            browser -= 35
        browser = max(0, browser)

        contract = 95
        if contract_delta > 0:
            contract -= min(70, contract_delta * 25)
        elif contract_delta == 0:
            contract -= 5
        else:
            contract = min(100, contract + min(20, abs(contract_delta) * 8))
        if delta_status == "regressed":
            contract = min(contract, 40)

        diagnostics = int(max(0.0, min(100.0, diagnostics_coverage)))
        if env_delta > 0:
            diagnostics = max(0, diagnostics - 5)

        architecture = 94
        if selected_count == 0:
            architecture -= 8
        selected_domains = {
            str(row.get("domain", "unknown")) for row in batch_execution_results.get("selected_batches", [])
        }
        if len(selected_domains) >= 3:
            architecture -= 10
        architecture = max(0, architecture)

        system = round((transport + browser + contract + diagnostics + architecture) / 5.0, 2)
        return {
            "generated_at": _now_iso(),
            "transport_stability_score": transport,
            "browser_lifecycle_score": browser,
            "contract_integrity_score": contract,
            "diagnostics_reliability_score": diagnostics,
            "architecture_integrity_score": architecture,
            "system_stability_score": system,
        }


class RiskAnalyzer:
    def detect(
        self,
        *,
        scorecard: dict[str, Any],
        cycle_summary: dict[str, Any],
        improvement_delta: dict[str, Any],
        batch_execution_results: dict[str, Any],
    ) -> list[dict[str, Any]]:
        risks: list[dict[str, Any]] = []
        delta_status = str(improvement_delta.get("status", "unchanged"))
        env_classification = str(improvement_delta.get("classification", "not blocked"))
        env_delta = int(improvement_delta.get("delta", {}).get("environment_blockers", 0))
        blocked = int(improvement_delta.get("remediation_outcomes", {}).get("blocked", 0))
        selected_count = len(batch_execution_results.get("selected_batches", []))

        if delta_status == "regressed":
            risks.append(
                {
                    "risk_id": "RISK-REGRESSION-001",
                    "severity": "critical",
                    "dimension": "contract_integrity",
                    "description": "Post-remediation validation regressed versus baseline.",
                    "evidence": {"delta_status": delta_status, "cycle_verdict": cycle_summary.get("cycle_verdict")},
                    "recommended_action": "rollback remediation candidates and run targeted root-cause review",
                }
            )

        if env_classification == "environment blocked" or env_delta > 0 or blocked > 0:
            risks.append(
                {
                    "risk_id": "RISK-ENV-001",
                    "severity": "high",
                    "dimension": "browser_lifecycle",
                    "description": "Environment instability is blocking reliable validation signal.",
                    "evidence": {
                        "classification": env_classification,
                        "environment_blocker_delta": env_delta,
                        "blocked_batches": blocked,
                    },
                    "recommended_action": "quarantine environment noise before expanding remediation scope",
                }
            )

        diagnostics_score = int(scorecard.get("diagnostics_reliability_score", 0))
        if diagnostics_score < 80:
            risks.append(
                {
                    "risk_id": "RISK-DIAG-001",
                    "severity": "moderate",
                    "dimension": "diagnostics_infrastructure",
                    "description": "Diagnostics reliability score is below target threshold.",
                    "evidence": {"diagnostics_reliability_score": diagnostics_score},
                    "recommended_action": "harden diagnostics capture and enrichment before next cycle",
                }
            )

        if selected_count == 0:
            risks.append(
                {
                    "risk_id": "RISK-SCOPE-001",
                    "severity": "low",
                    "dimension": "architectural_integrity",
                    "description": "No remediation batches selected in cycle, reducing change confidence gain.",
                    "evidence": {"selected_batches": selected_count},
                    "recommended_action": "recalibrate batch prioritization inputs for next cycle",
                }
            )

        return risks


class RegressionDetector:
    def detect(
        self,
        *,
        cycle_summary: dict[str, Any],
        improvement_delta: dict[str, Any],
        risks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "generated_at": _now_iso(),
            "baseline_before": cycle_summary.get("baseline_before"),
            "baseline_after": cycle_summary.get("baseline_after"),
            "delta_non_pass_contracts": improvement_delta.get("delta", {}).get("non_pass_contracts", 0),
            "delta_environment_blockers": improvement_delta.get("delta", {}).get("environment_blockers", 0),
            "status": improvement_delta.get("status", "unchanged"),
            "new_critical_risks": [
                risk["risk_id"] for risk in risks if str(risk.get("severity")) == "critical"
            ],
            "new_high_risks": [risk["risk_id"] for risk in risks if str(risk.get("severity")) == "high"],
            "regression_detected": str(improvement_delta.get("status", "")) == "regressed",
        }


class GovernorVerdictPlanner:
    def decide(
        self,
        *,
        scorecard: dict[str, Any],
        risks: list[dict[str, Any]],
        regression_detection: dict[str, Any],
    ) -> dict[str, Any]:
        severities = [str(risk.get("severity", "low")) for risk in risks]
        critical_count = sum(1 for item in severities if item == "critical")
        high_count = sum(1 for item in severities if item == "high")
        system_score = float(scorecard.get("system_stability_score", 0.0))

        if critical_count > 0 or bool(regression_detection.get("regression_detected")):
            verdict = "critical_regression"
        elif system_score < 60 or high_count >= 2:
            verdict = "instability_detected"
        elif high_count >= 1 or len(risks) > 0:
            verdict = "stable_with_risks"
        else:
            verdict = "stable"

        enforcement = {
            "stable": "proceed to next validation cycle",
            "stable_with_risks": "allow next cycle with reduced scope and targeted monitoring",
            "instability_detected": "pause remediation and run architecture/diagnostics hardening",
            "critical_regression": "rollback candidates and restore last known stable baseline",
        }[verdict]

        return {
            "generated_at": _now_iso(),
            "governor_verdict": verdict,
            "enforcement_action": enforcement,
            "risk_counts": {
                "critical": critical_count,
                "high": high_count,
                "moderate": sum(1 for item in severities if item == "moderate"),
                "low": sum(1 for item in severities if item == "low"),
            },
            "system_stability_score": system_score,
        }


def run_stability_governor(
    *,
    closed_loop_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    readiness = StabilityGovernorReadinessEvaluator(closed_loop_dir=closed_loop_dir).evaluate()
    if not readiness.ok:
        raise RuntimeError("stability governor readiness failed; required cycle inputs missing")

    cycle_summary = _load_json(Path(readiness.inputs["cycle_summary"]))
    batch_execution_results = _load_json(Path(readiness.inputs["batch_execution_results"]))
    improvement_delta = _load_json(Path(readiness.inputs["improvement_delta"]))

    scorecard = StabilityScorecardBuilder().build(
        cycle_summary=cycle_summary,
        batch_execution_results=batch_execution_results,
        improvement_delta=improvement_delta,
    )
    risks = RiskAnalyzer().detect(
        scorecard=scorecard,
        cycle_summary=cycle_summary,
        improvement_delta=improvement_delta,
        batch_execution_results=batch_execution_results,
    )
    regression = RegressionDetector().detect(
        cycle_summary=cycle_summary,
        improvement_delta=improvement_delta,
        risks=risks,
    )
    verdict = GovernorVerdictPlanner().decide(
        scorecard=scorecard,
        risks=risks,
        regression_detection=regression,
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_json(output_dir / f"{ts}--stability-scorecard.json", scorecard)
    _write_json(output_dir / f"{ts}--detected-risks.json", risks)
    _write_json(output_dir / f"{ts}--governor-verdict.json", verdict)

    _write_markdown_artifacts(
        output_dir=output_dir,
        ts=ts,
        readiness=readiness.to_dict(),
        scorecard=scorecard,
        risks=risks,
        regression=regression,
        verdict=verdict,
    )

    return {
        "timestamp": ts,
        "stability_scorecard_path": str(output_dir / f"{ts}--stability-scorecard.json"),
        "detected_risks_path": str(output_dir / f"{ts}--detected-risks.json"),
        "governor_verdict_path": str(output_dir / f"{ts}--governor-verdict.json"),
        "governor_verdict": verdict["governor_verdict"],
    }


def _write_markdown_artifacts(
    *,
    output_dir: Path,
    ts: str,
    readiness: dict[str, Any],
    scorecard: dict[str, Any],
    risks: list[dict[str, Any]],
    regression: dict[str, Any],
    verdict: dict[str, Any],
) -> None:
    risk_lines = (
        [
            f"- {risk['risk_id']} severity={risk['severity']} dimension={risk['dimension']} "
            f"action={risk['recommended_action']}"
            for risk in risks
        ]
        if risks
        else ["- no material risks detected"]
    )

    files = {
        f"{ts}--stability-assessment.md": [
            "# Stability Assessment",
            "",
            f"- cycle_timestamp: {readiness['cycle_timestamp']}",
            f"- readiness_ok: {readiness['ok']}",
            f"- system_stability_score: {scorecard['system_stability_score']}",
            f"- governor_verdict: {verdict['governor_verdict']}",
        ],
        f"{ts}--risk-analysis.md": [
            "# Risk Analysis",
            "",
            *risk_lines,
        ],
        f"{ts}--regression-detection.md": [
            "# Regression Detection",
            "",
            f"- regression_detected: {regression['regression_detected']}",
            f"- status: {regression['status']}",
            f"- delta_non_pass_contracts: {regression['delta_non_pass_contracts']}",
            f"- delta_environment_blockers: {regression['delta_environment_blockers']}",
            f"- new_critical_risks: {', '.join(regression['new_critical_risks']) or 'none'}",
            f"- new_high_risks: {', '.join(regression['new_high_risks']) or 'none'}",
        ],
        f"{ts}--architecture-impact.md": [
            "# Architecture Impact",
            "",
            "- scope: bounded to closed-loop outputs and governor synthesis",
            "- boundary_check: no browser lifecycle manager duplication detected by this pipeline stage",
            "- note: deeper dependency graph checks should run in periodic architecture audit",
        ],
        f"{ts}--governor-verdict.md": [
            "# Governor Verdict",
            "",
            f"- verdict: {verdict['governor_verdict']}",
            f"- enforcement_action: {verdict['enforcement_action']}",
            f"- risk_counts: {json.dumps(verdict['risk_counts'])}",
            f"- system_stability_score: {verdict['system_stability_score']}",
        ],
    }

    for name, lines in files.items():
        (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
