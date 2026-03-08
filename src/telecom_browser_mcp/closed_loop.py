from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {path}")
    return matches[-1]


def _first(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {path}")
    return matches[0]


def _safe_latest_json(path: Path, pattern: str) -> dict[str, Any] | None:
    matches = sorted(path.glob(pattern))
    if not matches:
        return None
    return _load_json(matches[-1])


@dataclass(slots=True)
class ReadinessResult:
    ok: bool
    checks: dict[str, bool]
    inputs: dict[str, str]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": self.checks,
            "inputs": self.inputs,
            "generated_at": self.generated_at,
        }


class CycleReadinessEvaluator:
    def __init__(
        self,
        *,
        validation_dir: Path,
        validation_diagnostics_dir: Path,
        signatures_dir: Path,
        prioritization_dir: Path,
        remediation_dir: Path,
    ) -> None:
        self.validation_dir = validation_dir
        self.validation_diagnostics_dir = validation_diagnostics_dir
        self.signatures_dir = signatures_dir
        self.prioritization_dir = prioritization_dir
        self.remediation_dir = remediation_dir

    def evaluate(self) -> ReadinessResult:
        inputs: dict[str, str] = {}
        checks: dict[str, bool] = {}
        required = {
            "validation_summary": (self.validation_dir, "*--validation-summary.json"),
            "enriched_validation_summary": (
                self.validation_diagnostics_dir,
                "enriched-validation-summary.json",
            ),
            "root_cause_summary": (self.validation_diagnostics_dir, "root-cause-summary.json"),
            "failure_signatures": (self.signatures_dir, "*--failure-signatures.json"),
            "signature_priority_ranking": (
                self.prioritization_dir,
                "*--signature-priority-ranking.json",
            ),
            "recommended_batches": (self.prioritization_dir, "*--recommended-batches.json"),
            "batch_status": (self.remediation_dir, "*--batch-status.json"),
            "rerun_summary": (self.remediation_dir, "*--rerun-summary.json"),
        }

        for key, (directory, pattern) in required.items():
            try:
                path = _latest(directory, pattern)
                checks[key] = True
                inputs[key] = str(path)
            except FileNotFoundError:
                checks[key] = False
                inputs[key] = ""

        return ReadinessResult(
            ok=all(checks.values()),
            checks=checks,
            inputs=inputs,
            generated_at=_now_iso(),
        )


class BatchSelectionCoordinator:
    PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    DOMAIN_ORDER = {
        "product_logic": 0,
        "browser_lifecycle_or_harness": 1,
        "diagnostics_pipeline": 2,
        "contract_definition": 3,
        "environment_or_ci": 4,
    }

    def select(
        self,
        *,
        recommended_batches: list[dict[str, Any]],
        ranked_signatures: list[dict[str, Any]],
        max_batches: int = 2,
    ) -> dict[str, Any]:
        score_by_sig = {
            str(row.get("signature_id", "")): int(row.get("score", 0))
            for row in ranked_signatures
        }

        scored: list[dict[str, Any]] = []
        for batch in recommended_batches:
            signature_ids = [str(item) for item in batch.get("target_signature_ids", [])]
            max_score = max((score_by_sig.get(sig, 0) for sig in signature_ids), default=0)
            scored.append(
                {
                    **batch,
                    "max_signature_score": max_score,
                }
            )

        scored.sort(
            key=lambda item: (
                self.PRIORITY_ORDER.get(str(item.get("priority_bucket", "P4")), 9),
                -int(item.get("max_signature_score", 0)),
                self.DOMAIN_ORDER.get(str(item.get("domain", "environment_or_ci")), 9),
            )
        )

        selected: list[dict[str, Any]] = []
        deferred: list[dict[str, Any]] = []
        for row in scored:
            bucket = str(row.get("priority_bucket", "P4"))
            domain = str(row.get("domain", "environment_or_ci"))
            if bucket in {"P0", "P1"} and domain != "environment_or_ci" and len(selected) < max_batches:
                selected.append(
                    {
                        **row,
                        "selection_reason": "high priority non-environment failure with strong evidence",
                    }
                )
                continue
            deferred.append(
                {
                    **row,
                    "defer_reason": "lower priority or out-of-scope for this small cycle",
                }
            )

        return {
            "selected_batches": selected,
            "deferred_batches": deferred,
            "selection_rules": [
                "prefer P0/P1",
                "exclude environment_or_ci from first cycle selection",
                "cap selected batches to small cycle limit",
            ],
        }


class PostRemediationDeltaAnalyzer:
    def analyze(
        self,
        *,
        before_validation: dict[str, Any],
        after_validation: dict[str, Any],
        enriched_summary: dict[str, Any],
        ranking: dict[str, Any],
        batch_status: dict[str, Any],
        runtime_transport_classification: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        before_non_pass = (
            int(before_validation.get("total_fail", 0))
            + int(before_validation.get("total_partial", 0))
            + int(before_validation.get("total_inconclusive", 0))
        )
        after_non_pass = (
            int(after_validation.get("total_fail", 0))
            + int(after_validation.get("total_partial", 0))
            + int(after_validation.get("total_inconclusive", 0))
        )

        before_env = len(before_validation.get("environment_blockers", []))
        after_env = len(after_validation.get("environment_blockers", []))

        ranked = ranking.get("ranked_signatures", [])
        top_signatures = [item.get("signature_name") for item in ranked[:3]]
        fixed_count = sum(1 for value in batch_status.values() if value == "fixed")
        partial_count = sum(1 for value in batch_status.values() if value == "partially fixed")
        blocked_count = sum(1 for value in batch_status.values() if "blocked" in str(value))

        if after_non_pass < before_non_pass:
            status = "fixed" if (before_non_pass - after_non_pass) >= 2 else "partially improved"
        elif after_non_pass == before_non_pass:
            status = "unchanged"
        else:
            status = "regressed"

        runtime_class = str((runtime_transport_classification or {}).get("classification", "unknown"))
        runtime_class_norm = runtime_class.strip().lower()
        runtime_env_quarantined = runtime_class_norm in {
            "sandbox_only_execution_blocker",
            "sandbox_runner_transport_blocker",
        }

        if runtime_env_quarantined:
            env_classification = "runtime transport sandbox blocked (quarantined)"
        elif after_env > 0 and blocked_count > 0:
            env_classification = "environment blocked"
        else:
            env_classification = "not blocked"

        return {
            "generated_at": _now_iso(),
            "before": {
                "timestamp": before_validation.get("timestamp"),
                "non_pass_contracts": before_non_pass,
                "environment_blockers": before_env,
            },
            "after": {
                "timestamp": after_validation.get("timestamp"),
                "non_pass_contracts": after_non_pass,
                "environment_blockers": after_env,
            },
            "delta": {
                "non_pass_contracts": after_non_pass - before_non_pass,
                "environment_blockers": after_env - before_env,
            },
            "diagnostics_coverage_score": enriched_summary.get("diagnostics_coverage_score", 0.0),
            "top_signatures": top_signatures,
            "remediation_outcomes": {
                "fixed": fixed_count,
                "partially_fixed": partial_count,
                "blocked": blocked_count,
            },
            "status": status,
            "classification": env_classification,
            "runtime_transport_classification": runtime_class,
            "runtime_environment_quarantined": runtime_env_quarantined,
        }


class NextCyclePlanner:
    def evaluate_cycle(self, delta: dict[str, Any]) -> dict[str, Any]:
        status = str(delta.get("status", "inconclusive"))
        diagnostics = float(delta.get("diagnostics_coverage_score", 0.0))
        blocked = int(delta.get("remediation_outcomes", {}).get("blocked", 0))
        after_non_pass = int(delta.get("after", {}).get("non_pass_contracts", 0))
        env_quarantined = bool(delta.get("runtime_environment_quarantined", False))

        if status == "regressed":
            verdict = "regression detected"
        elif not env_quarantined and blocked > 0 and status in {"unchanged", "partially improved"}:
            verdict = "blocked by environment"
        elif diagnostics < 10.0 and status in {"unchanged", "partially improved"}:
            verdict = "blocked by diagnostics"
        elif status == "fixed":
            verdict = "meaningful improvement achieved"
        elif status == "partially improved":
            verdict = "partial improvement continue"
        elif after_non_pass <= 2:
            verdict = "stable enough for beta"
        else:
            verdict = "partial improvement continue"

        if verdict in {"blocked by diagnostics", "blocked by environment"}:
            next_action = "focus on diagnostics hardening"
        elif verdict == "regression detected":
            next_action = "run another remediation cycle"
        elif verdict == "stable enough for beta":
            next_action = "stop for beta readiness"
        else:
            next_action = "run another remediation cycle"

        return {
            "generated_at": _now_iso(),
            "cycle_verdict": verdict,
            "next_action": next_action,
            "questions": [
                "did failures decrease?",
                "did diagnostics improve?",
                "were new regressions introduced?",
            ],
        }


def run_closed_loop_cycle(
    *,
    validation_dir: Path,
    validation_diagnostics_dir: Path,
    signatures_dir: Path,
    prioritization_dir: Path,
    remediation_dir: Path,
    output_dir: Path,
    max_batches: int = 2,
    investigations_dir: Path | None = None,
) -> dict[str, Any]:
    readiness = CycleReadinessEvaluator(
        validation_dir=validation_dir,
        validation_diagnostics_dir=validation_diagnostics_dir,
        signatures_dir=signatures_dir,
        prioritization_dir=prioritization_dir,
        remediation_dir=remediation_dir,
    ).evaluate()
    if not readiness.ok:
        raise RuntimeError("readiness check failed; required inputs missing")

    ranked = _load_json(Path(readiness.inputs["signature_priority_ranking"]))
    batches = _load_json(Path(readiness.inputs["recommended_batches"]))
    batch_selection = BatchSelectionCoordinator().select(
        recommended_batches=batches.get("recommended_batches", []),
        ranked_signatures=ranked.get("ranked_signatures", []),
        max_batches=max_batches,
    )

    before_validation = _load_json(_first(validation_dir, "*--validation-summary.json"))
    after_validation = _load_json(Path(readiness.inputs["validation_summary"]))
    enriched = _load_json(Path(readiness.inputs["enriched_validation_summary"]))
    batch_status = _load_json(Path(readiness.inputs["batch_status"]))
    runtime_transport = None
    if investigations_dir is not None:
        runtime_transport = _safe_latest_json(investigations_dir, "*--runtime-transport-classification.json")

    delta = PostRemediationDeltaAnalyzer().analyze(
        before_validation=before_validation,
        after_validation=after_validation,
        enriched_summary=enriched,
        ranking=ranked,
        batch_status=batch_status,
        runtime_transport_classification=runtime_transport,
    )
    verdict = NextCyclePlanner().evaluate_cycle(delta)

    cycle_summary = {
        "generated_at": _now_iso(),
        "readiness": readiness.to_dict(),
        "baseline_before": str(_first(validation_dir, "*--validation-summary.json")),
        "baseline_after": readiness.inputs["validation_summary"],
        "selected_batch_ids": [item["batch_id"] for item in batch_selection["selected_batches"]],
        "delta_status": delta["status"],
        "cycle_verdict": verdict["cycle_verdict"],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    _write_cycle_documents(
        output_dir=output_dir,
        ts=ts,
        readiness=readiness.to_dict(),
        batch_selection=batch_selection,
        delta=delta,
        verdict=verdict,
        cycle_summary=cycle_summary,
    )

    _write_json(output_dir / f"{ts}--cycle-summary.json", cycle_summary)
    _write_json(output_dir / f"{ts}--batch-execution-results.json", batch_selection)
    _write_json(output_dir / f"{ts}--improvement-delta.json", delta)

    return {
        "timestamp": ts,
        "cycle_summary_path": str(output_dir / f"{ts}--cycle-summary.json"),
        "batch_execution_results_path": str(output_dir / f"{ts}--batch-execution-results.json"),
        "improvement_delta_path": str(output_dir / f"{ts}--improvement-delta.json"),
        "cycle_verdict": verdict["cycle_verdict"],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_cycle_documents(
    *,
    output_dir: Path,
    ts: str,
    readiness: dict[str, Any],
    batch_selection: dict[str, Any],
    delta: dict[str, Any],
    verdict: dict[str, Any],
    cycle_summary: dict[str, Any],
) -> None:
    selected_rows = batch_selection.get("selected_batches", [])
    deferred_rows = batch_selection.get("deferred_batches", [])

    files = {
        f"{ts}--readiness-check.md": [
            "# Readiness Check",
            "",
            f"- ok: {readiness['ok']}",
            *[f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in readiness["checks"].items()],
        ],
        f"{ts}--selected-batches.md": [
            "# Selected Batches",
            "",
            "## Selected",
            *[
                (
                    f"- {row['batch_id']} {row['priority_bucket']} {row['domain']} "
                    f"score={row['max_signature_score']} reason={row['selection_reason']}"
                )
                for row in selected_rows
            ],
            "",
            "## Deferred",
            *[
                f"- {row['batch_id']} {row['priority_bucket']} {row['domain']} reason={row['defer_reason']}"
                for row in deferred_rows
            ],
        ],
        f"{ts}--cycle-plan.md": [
            "# Cycle Plan",
            "",
            f"- generated_at: {cycle_summary['generated_at']}",
            f"- baseline_before: `{cycle_summary['baseline_before']}`",
            f"- baseline_after: `{cycle_summary['baseline_after']}`",
            f"- selected_batch_ids: {', '.join(cycle_summary['selected_batch_ids']) or 'none'}",
            "",
            "Planned stages:",
            "1. Validate readiness inputs.",
            "2. Select small remediation batch set.",
            "3. Execute/remap remediation evidence.",
            "4. Compute post-remediation delta and verdict.",
        ],
        f"{ts}--execution-log.md": [
            "# Execution Log",
            "",
            "Execution mode: evidence-linked advisory loop.",
            f"- selected_batches: {len(selected_rows)}",
            f"- deferred_batches: {len(deferred_rows)}",
            f"- remediation_outcomes: {json.dumps(delta['remediation_outcomes'])}",
        ],
        f"{ts}--post-remediation-validation.md": [
            "# Post-Remediation Validation",
            "",
            f"- before_timestamp: {delta['before']['timestamp']}",
            f"- after_timestamp: {delta['after']['timestamp']}",
            f"- before_non_pass_contracts: {delta['before']['non_pass_contracts']}",
            f"- after_non_pass_contracts: {delta['after']['non_pass_contracts']}",
            f"- delta_non_pass_contracts: {delta['delta']['non_pass_contracts']}",
            f"- diagnostics_coverage_score: {delta['diagnostics_coverage_score']}",
            f"- classification: {delta['classification']}",
            f"- status: {delta['status']}",
        ],
        f"{ts}--cycle-verdict.md": [
            "# Cycle Verdict",
            "",
            f"- verdict: {verdict['cycle_verdict']}",
            f"- next_action: {verdict['next_action']}",
        ],
        f"{ts}--next-cycle-recommendations.md": [
            "# Next Cycle Recommendations",
            "",
            *[f"- {question}" for question in verdict["questions"]],
            f"- recommended_action: {verdict['next_action']}",
        ],
    }

    for name, lines in files.items():
        (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
