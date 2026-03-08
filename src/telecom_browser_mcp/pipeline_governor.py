from __future__ import annotations

import json
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


def _extract_ts(path: Path) -> str:
    if "--" not in path.name:
        raise ValueError(f"cannot parse timestamp from {path.name}")
    return path.name.split("--", 1)[0]


def _safe_latest_json(path: Path, pattern: str) -> tuple[dict[str, Any] | None, str]:
    try:
        file_path = _latest(path, pattern)
    except FileNotFoundError:
        return None, ""
    return _load_json(file_path), str(file_path)


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


class PipelineVerdictCollector:
    def __init__(
        self,
        *,
        closed_loop_dir: Path,
        stability_dir: Path,
        guardrails_dir: Path,
        learning_dir: Path,
        drift_dir: Path,
        investigations_dir: Path,
        release_hardening_dir: Path,
        live_verification_dir: Path,
    ) -> None:
        self.closed_loop_dir = closed_loop_dir
        self.stability_dir = stability_dir
        self.guardrails_dir = guardrails_dir
        self.learning_dir = learning_dir
        self.drift_dir = drift_dir
        self.investigations_dir = investigations_dir
        self.release_hardening_dir = release_hardening_dir
        self.live_verification_dir = live_verification_dir

    def collect(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "generated_at": _now_iso(),
            "closed_loop": {
                "available": False,
                "reason": "closed-loop artifacts not found",
                "source_paths": {},
            },
            "stability": {
                "available": False,
                "reason": "stability governor artifacts not found",
                "source_paths": {},
            },
            "guardrails": {
                "available": False,
                "reason": "architecture guardrails artifacts not found",
                "source_paths": {},
            },
            "learning": {
                "available": False,
                "reason": "cross-cycle learning artifacts not found",
                "source_paths": {},
            },
            "drift": {
                "available": False,
                "reason": "system drift artifacts not found",
                "source_paths": {},
            },
            "release_hardening": {
                "available": False,
                "reason": "release hardening artifacts not found",
                "release_hardening_verdict": "release_hardening_not_available",
                "release_track_allowed": False,
                "release_block_reason": [],
                "release_hardening_required": True,
                "missing_artifacts": [],
                "source_paths": {},
            },
            "live_verification": {
                "available": False,
                "reason": "live verification artifacts not found",
                "live_verification_verdict": "live_verification_not_available",
                "blocking_reasons": [],
                "source_paths": {},
            },
            "meta": {
                "cycle_count": len(sorted(self.closed_loop_dir.glob("*--cycle-summary.json"))),
            },
        }

        try:
            cycle_summary_path = _latest(self.closed_loop_dir, "*--cycle-summary.json")
            ts = _extract_ts(cycle_summary_path)
            cycle_summary = _load_json(cycle_summary_path)
            improvement_delta, improvement_path = _safe_latest_json(
                self.closed_loop_dir, f"{ts}--improvement-delta.json"
            )
            batch_results, batch_results_path = _safe_latest_json(
                self.closed_loop_dir, f"{ts}--batch-execution-results.json"
            )
            transport_triage, transport_triage_path = _safe_latest_json(
                self.closed_loop_dir, f"{ts}--transport-triage.json"
            )
            runtime_transport, runtime_transport_path = _safe_latest_json(
                self.investigations_dir, "*--runtime-transport-classification.json"
            )
            cycle_verdict_file = self.closed_loop_dir / f"{ts}--cycle-verdict.json"
            cycle_verdict_text = ""
            if cycle_verdict_file.exists():
                cycle_verdict_text = str(_load_json(cycle_verdict_file).get("cycle_verdict", ""))
            else:
                cycle_verdict_text = str(cycle_summary.get("cycle_verdict", ""))

            env_failures = []
            for row in cycle_summary.get("environment_blockers", []):
                if isinstance(row, str):
                    env_failures.append(row)
            env_delta = int((improvement_delta or {}).get("delta", {}).get("environment_blockers", 0))

            payload["closed_loop"] = {
                "available": True,
                "cycle_timestamp": ts,
                "cycle_verdict": cycle_verdict_text,
                "improvement_delta": improvement_delta or {},
                "selected_batches": (batch_results or {}).get("selected_batches", []),
                "runtime_transport_classification": (
                    (transport_triage or {}).get("classification")
                    or (runtime_transport or {}).get("classification")
                    or "unknown"
                ),
                "environment_failures": env_failures,
                "environment_failure_delta": env_delta,
                "source_paths": {
                    "cycle_summary": str(cycle_summary_path),
                    "improvement_delta": improvement_path,
                    "batch_execution_results": batch_results_path,
                    "transport_triage": transport_triage_path,
                    "runtime_transport_classification": runtime_transport_path,
                },
            }
        except FileNotFoundError:
            pass

        scorecard, scorecard_path = _safe_latest_json(self.stability_dir, "*--stability-scorecard.json")
        risks, risks_path = _safe_latest_json(self.stability_dir, "*--detected-risks.json")
        verdict, verdict_path = _safe_latest_json(self.stability_dir, "*--governor-verdict.json")
        if scorecard or verdict:
            payload["stability"] = {
                "available": True,
                "stability_verdict": (verdict or {}).get("governor_verdict", "unknown"),
                "system_stability_score": (
                    (scorecard or {}).get("system_stability_score")
                    if scorecard
                    else (verdict or {}).get("system_stability_score", 0)
                ),
                "detected_risks": risks or [],
                "regression_flags": {
                    "critical_risk_count": sum(
                        1 for row in (risks or []) if _normalize_text(row.get("severity")) == "critical"
                    ),
                    "high_risk_count": sum(
                        1 for row in (risks or []) if _normalize_text(row.get("severity")) == "high"
                    ),
                    "critical_regression": _normalize_text((verdict or {}).get("governor_verdict"))
                    == "critical_regression",
                },
                "source_paths": {
                    "stability_scorecard": scorecard_path,
                    "detected_risks": risks_path,
                    "governor_verdict": verdict_path,
                },
            }

        precheck, precheck_path = _safe_latest_json(self.guardrails_dir, "*--precheck-verdict.json")
        postcheck, postcheck_path = _safe_latest_json(self.guardrails_dir, "*--postcheck-verdict.json")
        if precheck or postcheck:
            resolved_precheck = precheck or {}
            resolved_postcheck = postcheck or {}
            payload["guardrails"] = {
                "available": True,
                "precheck_verdict": str(resolved_precheck.get("verdict", "unknown")),
                "postcheck_verdict": str(resolved_postcheck.get("verdict", "unknown")),
                "boundary_violation_flags": resolved_postcheck.get("boundary_violation_flags", []),
                "dependency_violation_flags": resolved_postcheck.get("dependency_violation_flags", []),
                "contract_layer_violation_flags": resolved_postcheck.get("contract_layer_violation_flags", []),
                "source_paths": {
                    "precheck_verdict": precheck_path,
                    "postcheck_verdict": postcheck_path,
                },
            }

        learning, learning_path = _safe_latest_json(self.learning_dir, "*--learning-summary.json")
        if learning:
            payload["learning"] = {
                "available": True,
                "signature_updates": learning.get("signature_updates", []),
                "prioritization_adjustments": learning.get("prioritization_adjustments", []),
                "diagnostics_gap_recommendations": learning.get("diagnostics_gap_recommendations", []),
                "stability_heuristic_adjustments": learning.get("stability_heuristic_adjustments", []),
                "source_paths": {"learning_summary": learning_path},
            }

        drift_report, drift_report_path = _safe_latest_json(self.drift_dir, "*--architecture-drift-report.json")
        drift_scorecard, drift_scorecard_path = _safe_latest_json(self.drift_dir, "*--drift-scorecard.json")
        if drift_report or drift_scorecard:
            report = drift_report or {}
            score = drift_scorecard or {}
            payload["drift"] = {
                "available": True,
                "architecture_drift_score": score.get("architecture_drift_score", report.get("architecture_drift_score", 0)),
                "drift_severity": score.get("drift_severity", report.get("drift_severity", "unknown")),
                "blocked_subsystems": report.get("blocked_subsystems", []),
                "refactoring_recommendations": report.get("refactoring_recommendations", []),
                "source_paths": {
                    "architecture_drift_report": drift_report_path,
                    "drift_scorecard": drift_scorecard_path,
                },
            }

        release_verdict_path = self.release_hardening_dir / "release-hardening-verdict.json"
        release_checks_path = self.release_hardening_dir / "release-check-results.json"
        release_risks_path = self.release_hardening_dir / "release-risk-register.json"
        release_files = {
            "release_hardening_verdict": release_verdict_path,
            "release_check_results": release_checks_path,
            "release_risk_register": release_risks_path,
        }
        existing_release_files = {key: path for key, path in release_files.items() if path.exists()}
        if existing_release_files:
            verdict_payload = _load_json(release_verdict_path) if release_verdict_path.exists() else {}
            checks_payload = _load_json(release_checks_path) if release_checks_path.exists() else {}
            risks_payload = _load_json(release_risks_path) if release_risks_path.exists() else {}
            missing_artifacts = [str(path) for path in release_files.values() if not path.exists()]

            resolved_verdict = _normalize_text(verdict_payload.get("verdict"))
            if not resolved_verdict:
                resolved_verdict = "release_hardening_incomplete"
            elif missing_artifacts and resolved_verdict == "release_ready":
                resolved_verdict = "release_hardening_incomplete"

            release_block_reasons: list[str] = []
            for item in verdict_payload.get("blocking_reasons", []):
                if isinstance(item, str):
                    release_block_reasons.append(item)

            for check in checks_payload.get("checks", []):
                if not isinstance(check, dict):
                    continue
                status = _normalize_text(check.get("status"))
                if status == "blocked":
                    check_id = str(check.get("check_id", "unknown_check"))
                    release_block_reasons.append(f"{check_id}_blocked")

            for risk in risks_payload.get("risks", []):
                if not isinstance(risk, dict):
                    continue
                if bool(risk.get("release_blocking")):
                    release_block_reasons.append(str(risk.get("risk_id", "unknown_risk")).lower())

            deduped_reasons: list[str] = []
            for reason in release_block_reasons:
                if reason not in deduped_reasons:
                    deduped_reasons.append(reason)

            payload["release_hardening"] = {
                "available": True,
                "release_hardening_verdict": resolved_verdict,
                "release_track_allowed": resolved_verdict == "release_ready",
                "release_block_reason": deduped_reasons,
                "release_hardening_required": resolved_verdict != "release_ready",
                "missing_artifacts": missing_artifacts,
                "source_paths": {
                    key: str(path)
                    for key, path in existing_release_files.items()
                },
            }

        live_verdict_path = self.live_verification_dir / "live-verification-verdict.json"
        live_results_path = self.live_verification_dir / "live-check-results.json"
        live_summary_path = self.live_verification_dir / "live-verification-summary.json"
        live_files = {
            "live_verification_verdict": live_verdict_path,
            "live_check_results": live_results_path,
            "live_verification_summary": live_summary_path,
        }
        existing_live_files = {key: path for key, path in live_files.items() if path.exists()}
        if existing_live_files:
            verdict_payload = _load_json(live_verdict_path) if live_verdict_path.exists() else {}
            verdict_name = _normalize_text(verdict_payload.get("verdict"))
            if not verdict_name:
                verdict_name = "live_verification_incomplete"

            blocking_reasons: list[str] = []
            for reason in verdict_payload.get("blocking_reasons", []):
                if isinstance(reason, str) and reason:
                    blocking_reasons.append(reason)

            payload["live_verification"] = {
                "available": True,
                "live_verification_verdict": verdict_name,
                "blocking_reasons": blocking_reasons,
                "source_paths": {key: str(path) for key, path in existing_live_files.items()},
            }

        return payload


class ConflictResolutionEngine:
    def resolve(self, *, collected: dict[str, Any]) -> dict[str, Any]:
        conflicts: list[dict[str, Any]] = []
        closed_loop = collected["closed_loop"]
        stability = collected["stability"]
        guardrails = collected["guardrails"]
        drift = collected["drift"]

        improved = _normalize_text(closed_loop.get("cycle_verdict")) in {
            "meaningful_improvement_achieved",
            "partial_improvement_continue",
            "stable_enough_for_beta",
        }
        runtime_class = _normalize_text(closed_loop.get("runtime_transport_classification"))
        runtime_block = (
            "ambiguous" in runtime_class
            or "unresolved" in runtime_class
            or _normalize_text(closed_loop.get("cycle_verdict")) == "blocked_by_runtime_environment"
        )
        postcheck = _normalize_text(guardrails.get("postcheck_verdict"))
        stability_verdict = _normalize_text(stability.get("stability_verdict"))
        drift_severity = _normalize_text(drift.get("drift_severity"))

        if improved and postcheck in {"block", "blocked", "failed", "guardrails_block"}:
            conflicts.append(
                {
                    "conflict_id": "CASE-A-VALIDATION-VS-ARCHITECTURE",
                    "classification": "blocked_by_architecture",
                    "summary": "Validation improved but architecture guardrails post-check blocked cycle.",
                }
            )

        if improved and stability_verdict in {"critical_regression", "instability_detected"}:
            conflicts.append(
                {
                    "conflict_id": "CASE-B-VALIDATION-VS-STABILITY",
                    "classification": "regression_detected",
                    "summary": "Validation improved but stability governor detected regression/instability.",
                }
            )

        if improved and stability_verdict in {"stable", "stable_with_risks"} and drift_severity == "severe":
            conflicts.append(
                {
                    "conflict_id": "CASE-C-STABILITY-VS-DRIFT",
                    "classification": "continue_with_architecture_constraints",
                    "summary": "Functional/stability signal improved but drift severity is severe.",
                }
            )

        if runtime_block:
            conflicts.append(
                {
                    "conflict_id": "CASE-D-RUNTIME-AMBIGUITY",
                    "classification": "blocked_by_runtime_environment",
                    "summary": "Validation signal is blocked by unresolved runtime transport ambiguity.",
                }
            )

        return {
            "generated_at": _now_iso(),
            "conflicts": conflicts,
            "has_conflicts": bool(conflicts),
        }


class NextActionPlanner:
    def plan(self, *, collected: dict[str, Any], global_verdict: str) -> dict[str, Any]:
        actions: list[dict[str, str]] = []
        blocked_actions: list[dict[str, str]] = []
        closed_loop = collected["closed_loop"]
        guardrails = collected["guardrails"]
        meta = collected["meta"]
        cycle_count = int(meta.get("cycle_count", 0))

        if not guardrails.get("available") or _normalize_text(guardrails.get("precheck_verdict")) not in {
            "pass",
            "passed",
            "ok",
            "guardrails_pass",
            "guardrails_warn",
        }:
            blocked_actions.append(
                {
                    "pipeline": "closed_loop_validation_remediation",
                    "reason": "architecture pre-check missing or not passed",
                }
            )
            actions.append(
                {
                    "pipeline": "architecture_guardrails_precheck",
                    "reason": "required before remediation cycle",
                }
            )
        else:
            actions.append(
                {
                    "pipeline": "closed_loop_validation_remediation",
                    "reason": "architecture pre-check satisfied",
                }
            )

        if closed_loop.get("available"):
            actions.append(
                {
                    "pipeline": "closed_loop_stability_governor",
                    "reason": "closed-loop cycle available for stability evaluation",
                }
            )
            actions.append(
                {
                    "pipeline": "architecture_guardrails_postcheck",
                    "reason": "post-remediation guardrail validation required",
                }
            )

        if cycle_count >= 2:
            actions.append(
                {
                    "pipeline": "cross_cycle_learning_engine",
                    "reason": "eligible by cycle cadence threshold (>=2 cycles)",
                }
            )

        if cycle_count >= 5 or global_verdict == "release_candidate":
            actions.append(
                {
                    "pipeline": "system_drift_detector",
                    "reason": "eligible by cadence/release policy",
                }
            )

        if global_verdict.startswith("blocked_"):
            blocked_actions.append(
                {
                    "pipeline": "expansionary_remediation",
                    "reason": "global verdict is blocked; limit scope until blocker cleared",
                }
            )
        if global_verdict == "blocked_by_live_verification":
            blocked_actions.append(
                {
                    "pipeline": "release_progression",
                    "reason": "live verification gate failed",
                }
            )
            actions.append(
                {
                    "pipeline": "remediate_live_verification_blockers",
                    "reason": "repair live verification blockers before release progression",
                }
            )
            actions.append(
                {
                    "pipeline": "controlled_live_verification_recheck",
                    "reason": "re-run live verification after remediation",
                }
            )
            actions.append(
                {
                    "pipeline": "pipeline_governor",
                    "reason": "re-evaluate global state after live verification refresh",
                }
            )
        release_hardening = collected.get("release_hardening", {})
        if global_verdict in {"blocked_by_release_hardening", "release_hardening_incomplete"}:
            blocked_actions.append(
                {
                    "pipeline": "release_progression",
                    "reason": "release hardening gate not satisfied",
                }
            )
            if global_verdict == "blocked_by_release_hardening":
                actions.append(
                    {
                        "pipeline": "release_hardening_remediation",
                        "reason": "remediate release blockers before release progression",
                    }
                )
            actions.append(
                {
                    "pipeline": "release_hardening_recheck",
                    "reason": "rerun release hardening checks after remediation",
                }
            )
            actions.append(
                {
                    "pipeline": "pipeline_governor",
                    "reason": "rerun governor after release hardening artifacts refresh",
                }
            )
        elif global_verdict == "release_candidate" and release_hardening.get("available"):
            actions.append(
                {
                    "pipeline": "release_progression",
                    "reason": "release hardening indicates release track is allowed",
                }
            )

        return {
            "generated_at": _now_iso(),
            "allowed_actions": actions,
            "blocked_actions": blocked_actions,
        }


class GovernorStateManager:
    def determine_state(self, *, collected: dict[str, Any], global_verdict: str) -> str:
        if global_verdict == "blocked_by_live_verification":
            return "live-verification-blocked"
        if global_verdict == "blocked_by_release_hardening":
            return "release-blocked"
        if global_verdict == "release_hardening_incomplete":
            return "release-hardening-required"
        if global_verdict in {"blocked_by_runtime_environment", "blocked_by_architecture", "blocked_by_stability", "blocked_by_drift_constraints"}:
            return "blocked"
        if global_verdict == "pause_for_human_review":
            return "paused"
        if global_verdict == "release_candidate":
            return "release-candidate"

        if not collected["guardrails"].get("available"):
            return "precheck-required"
        if not collected["closed_loop"].get("available"):
            return "validation-running"
        if not collected["stability"].get("available"):
            return "stability-required"
        return "postcheck-required"


class PipelineGovernor:
    def decide(self, *, collected: dict[str, Any], conflicts: dict[str, Any]) -> dict[str, Any]:
        closed_loop = collected["closed_loop"]
        stability = collected["stability"]
        guardrails = collected["guardrails"]
        drift = collected["drift"]
        release_hardening = collected.get("release_hardening", {})
        live_verification = collected.get("live_verification", {})

        runtime_class = _normalize_text(closed_loop.get("runtime_transport_classification"))
        runtime_block = "ambiguous" in runtime_class or "unresolved" in runtime_class

        postcheck = _normalize_text(guardrails.get("postcheck_verdict"))
        guardrails_block = postcheck in {"block", "blocked", "failed", "guardrails_block"}

        stability_verdict = _normalize_text(stability.get("stability_verdict"))
        stability_block = stability_verdict in {"critical_regression", "instability_detected"}

        drift_severity = _normalize_text(drift.get("drift_severity"))
        drift_block = drift_severity == "severe" and bool(drift.get("blocked_subsystems", []))

        if runtime_block:
            global_verdict = "blocked_by_runtime_environment"
        elif guardrails_block:
            global_verdict = "blocked_by_architecture"
        elif stability_block:
            global_verdict = "blocked_by_stability"
        elif drift_block:
            global_verdict = "blocked_by_drift_constraints"
        else:
            cycle_verdict = _normalize_text(closed_loop.get("cycle_verdict"))
            if cycle_verdict in {"stable_enough_for_beta", "release_candidate"}:
                global_verdict = "release_candidate"
            elif cycle_verdict == "meaningful_improvement_achieved":
                global_verdict = "safe_meaningful_improvement"
            elif cycle_verdict in {"partial_improvement_continue", "unchanged"}:
                global_verdict = "partial_improvement_continue"
            else:
                global_verdict = "partial_improvement_continue"

        release_hardening_verdict = _normalize_text(release_hardening.get("release_hardening_verdict"))
        if global_verdict == "release_candidate":
            if release_hardening_verdict == "release_blocked":
                global_verdict = "blocked_by_release_hardening"
            elif release_hardening_verdict in {"release_hardening_incomplete", "release_hardening_not_available", ""}:
                global_verdict = "release_hardening_incomplete"

        live_verification_verdict = _normalize_text(live_verification.get("live_verification_verdict"))
        live_verification_blocking_verdicts = {
            "blocked",
            "blocked_by_environment",
            "blocked_by_transport",
            "blocked_by_browser_runtime",
            "blocked_by_integration",
        }
        if global_verdict == "release_candidate" and live_verification_verdict in live_verification_blocking_verdicts:
            global_verdict = "blocked_by_live_verification"

        recommended_action = {
            "safe_meaningful_improvement": "continue cycle",
            "partial_improvement_continue": "narrow remediation scope",
            "blocked_by_runtime_environment": "investigate runtime",
            "blocked_by_architecture": "run architecture cleanup",
            "blocked_by_stability": "pause and analyze regression",
            "blocked_by_drift_constraints": "restrict subsystem changes",
            "blocked_by_release_hardening": "remediate_release_blockers",
            "blocked_by_live_verification": "remediate_live_verification_blockers",
            "release_hardening_incomplete": "complete_release_hardening_checks",
            "pause_for_human_review": "stop automated progression",
            "architecture_cleanup_required": "run architecture cleanup",
            "release_candidate": "run release hardening checks",
        }[global_verdict]

        release_track_allowed = bool(release_hardening.get("release_track_allowed", False))
        release_block_reason = list(release_hardening.get("release_block_reason", []))
        if global_verdict == "blocked_by_live_verification":
            release_track_allowed = False
            release_block_reason.append("live_verification_blocked")

        return {
            "generated_at": _now_iso(),
            "global_verdict": global_verdict,
            "recommended_global_action": recommended_action,
            "conflict_count": len(conflicts.get("conflicts", [])),
            "inputs_used": {
                "closed_loop_available": bool(closed_loop.get("available")),
                "stability_available": bool(stability.get("available")),
                "guardrails_available": bool(guardrails.get("available")),
                "drift_available": bool(drift.get("available")),
                "release_hardening_available": bool(release_hardening.get("available")),
            },
            "release_hardening_verdict": release_hardening_verdict or "release_hardening_not_available",
            "release_track_allowed": release_track_allowed,
            "release_block_reason": release_block_reason,
            "release_hardening_required": bool(release_hardening.get("release_hardening_required", True)),
            "live_verification_verdict": live_verification_verdict or "live_verification_not_available",
        }


def run_pipeline_governor(
    *,
    closed_loop_dir: Path,
    stability_dir: Path,
    guardrails_dir: Path,
    learning_dir: Path,
    drift_dir: Path,
    investigations_dir: Path,
    release_hardening_dir: Path | None = None,
    live_verification_dir: Path | None = None,
    output_dir: Path,
) -> dict[str, Any]:
    resolved_release_hardening_dir = release_hardening_dir or Path("docs/release-hardening/telecom-browser-mcp")
    resolved_live_verification_dir = (
        live_verification_dir
        if live_verification_dir is not None
        else resolved_release_hardening_dir.parent / "live-verification"
    )
    collector = PipelineVerdictCollector(
        closed_loop_dir=closed_loop_dir,
        stability_dir=stability_dir,
        guardrails_dir=guardrails_dir,
        learning_dir=learning_dir,
        drift_dir=drift_dir,
        investigations_dir=investigations_dir,
        release_hardening_dir=resolved_release_hardening_dir,
        live_verification_dir=resolved_live_verification_dir,
    )
    collected = collector.collect()
    conflicts = ConflictResolutionEngine().resolve(collected=collected)
    verdict = PipelineGovernor().decide(collected=collected, conflicts=conflicts)
    state = GovernorStateManager().determine_state(collected=collected, global_verdict=verdict["global_verdict"])
    next_actions = NextActionPlanner().plan(collected=collected, global_verdict=verdict["global_verdict"])

    output_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        output_dir / "governor-state.json",
        {
            "generated_at": _now_iso(),
            "state": state,
            "cycle_count": collected.get("meta", {}).get("cycle_count", 0),
            "latest_cycle_timestamp": collected.get("closed_loop", {}).get("cycle_timestamp", ""),
        },
    )
    _write_json(output_dir / "governor-verdict.json", verdict)
    _write_json(output_dir / "next-pipeline-actions.json", next_actions)
    _write_json(output_dir / "pipeline-conflicts.json", conflicts)

    _write_markdown(
        output_dir=output_dir,
        collected=collected,
        verdict=verdict,
        state=state,
        conflicts=conflicts,
        next_actions=next_actions,
    )

    return {
        "governor_state_path": str(output_dir / "governor-state.json"),
        "governor_verdict_path": str(output_dir / "governor-verdict.json"),
        "next_pipeline_actions_path": str(output_dir / "next-pipeline-actions.json"),
        "pipeline_conflicts_path": str(output_dir / "pipeline-conflicts.json"),
        "global_verdict": verdict["global_verdict"],
        "state": state,
    }


def _write_markdown(
    *,
    output_dir: Path,
    collected: dict[str, Any],
    verdict: dict[str, Any],
    state: str,
    conflicts: dict[str, Any],
    next_actions: dict[str, Any],
) -> None:
    conflict_lines = [
        f"- {row['conflict_id']}: {row['classification']} ({row['summary']})"
        for row in conflicts.get("conflicts", [])
    ] or ["- no conflict rules triggered"]

    allowed_lines = [
        f"- {row['pipeline']}: {row['reason']}" for row in next_actions.get("allowed_actions", [])
    ] or ["- none"]
    blocked_lines = [
        f"- {row['pipeline']}: {row['reason']}" for row in next_actions.get("blocked_actions", [])
    ] or ["- none"]

    files = {
        "governor-cycle-plan.md": [
            "# Governor Cycle Plan",
            "",
            f"- generated_at: {verdict['generated_at']}",
            f"- cycle_count: {collected.get('meta', {}).get('cycle_count', 0)}",
            f"- latest_cycle_timestamp: {collected.get('closed_loop', {}).get('cycle_timestamp', 'unknown')}",
            "- execution_order:",
            "  1) architecture guardrails pre-check",
            "  2) closed-loop validation/remediation",
            "  3) stability governor",
            "  4) architecture guardrails post-check",
            "  5) pipeline governor verdict",
        ],
        "governor-decision-log.md": [
            "# Governor Decision Log",
            "",
            f"- state: {state}",
            f"- global_verdict: {verdict['global_verdict']}",
            f"- recommended_global_action: {verdict['recommended_global_action']}",
            f"- conflict_count: {verdict['conflict_count']}",
            f"- runtime_transport_classification: {collected.get('closed_loop', {}).get('runtime_transport_classification', 'unknown')}",
            f"- stability_verdict: {collected.get('stability', {}).get('stability_verdict', 'unknown')}",
            f"- guardrails_postcheck: {collected.get('guardrails', {}).get('postcheck_verdict', 'unknown')}",
            f"- drift_severity: {collected.get('drift', {}).get('drift_severity', 'unknown')}",
            f"- release_hardening_verdict: {verdict.get('release_hardening_verdict', 'release_hardening_not_available')}",
            f"- live_verification_verdict: {verdict.get('live_verification_verdict', 'live_verification_not_available')}",
            f"- release_track_allowed: {verdict.get('release_track_allowed', False)}",
        ],
        "pipeline-conflict-resolution.md": [
            "# Pipeline Conflict Resolution",
            "",
            *conflict_lines,
        ],
        "global-cycle-verdict.md": [
            "# Global Cycle Verdict",
            "",
            f"- verdict: {verdict['global_verdict']}",
            f"- action: {verdict['recommended_global_action']}",
        ],
        "next-run-instructions.md": [
            "# Next Run Instructions",
            "",
            (
                "Release progression blocked by release hardening: "
                + ", ".join(verdict.get("release_block_reason", []))
                if verdict.get("global_verdict") == "blocked_by_release_hardening"
                else "Release hardening status: " + verdict.get("release_hardening_verdict", "release_hardening_not_available")
            ),
            "",
            "## Allowed Pipelines",
            *allowed_lines,
            "",
            "## Blocked Pipelines",
            *blocked_lines,
        ],
    }

    for file_name, lines in files.items():
        (output_dir / file_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
