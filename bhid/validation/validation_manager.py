"""
BHID Primary Validation Manager.

Coordinates all read-only operational validators (consistency, prediction, event,
persistence, replay, reporting), evaluates system readiness, and exports validation reports.
"""

from typing import Dict, Any, List, Optional
import json
import time
from pathlib import Path

from bhid.validation.validation_config import ValidationConfig
from bhid.validation.consistency_validator import ConsistencyValidator
from bhid.validation.prediction_validator import PredictionValidator
from bhid.validation.event_validator import EventValidator
from bhid.validation.persistence_validator import PersistenceValidator
from bhid.validation.replay_validator import ReplayValidator
from bhid.validation.reporting_validator import ReportingValidator
from bhid.validation.system_evaluator import SystemEvaluator

from bhid.replay.playback_loader import PlaybackLoader
from bhid.replay.playback_engine import PlaybackEngine
from bhid.reporting.reporting_manager import ReportingManager


class ValidationManager:
    """
    Primary operational validation coordinator (Read-Only).
    """

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.config.initialize_directories()

    def run_all_validations(
        self,
        session_id: str,
        storage_root: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Executes complete read-only validation suite across a historical session.
        """
        # 1. Load persisted session artifacts (Read-Only)
        loader = PlaybackLoader(session_id=session_id, storage_root=storage_root)
        meta = loader.load_session_metadata()
        preds = loader.load_predictions()
        analytics = loader.load_analytics_snapshots()
        events = loader.load_events()
        session_dir = loader.session_dir

        # 2. Load Phase 5B Replay frames (Read-Only)
        pe = PlaybackEngine(session_id=session_id, storage_root=storage_root)
        replay_frames = pe.replay_all()

        # 3. Load Phase 5C Operational Report (Read-Only)
        rm = ReportingManager()
        report = rm.generate_report(session_id=session_id, storage_root=storage_root, export=False)
        report_dict = report.to_dict()
        md_content = report.to_markdown()

        # 4. Run validators (Read-Only)
        res_consistency = ConsistencyValidator.validate_pipeline_schemas(preds, analytics, events)
        res_prediction = PredictionValidator.validate_predictions(preds)
        res_event = EventValidator.validate_events(events)
        res_persistence = PersistenceValidator.validate_persistence(session_dir)
        res_replay = ReplayValidator.validate_replay(preds, analytics, events, replay_frames)
        res_reporting = ReportingValidator.validate_reporting(report_dict, preds, analytics, events, md_content)

        val_results = {
            "schema_consistency": res_consistency,
            "prediction_integrity": res_prediction,
            "event_lifecycle": res_event,
            "persistence_isolation": res_persistence,
            "replay_determinism": res_replay,
            "reporting_accuracy": res_reporting
        }

        # 5. Evaluate System Readiness
        evaluation = SystemEvaluator.evaluate_system(val_results, self.config)
        evaluation["session_id"] = session_id
        evaluation["validation_results"] = val_results
        evaluation["timestamp"] = time.time()

        return evaluation

    def export_validation_report(
        self,
        evaluation_result: Dict[str, Any],
        file_prefix: str = "validation_report"
    ) -> Dict[str, Optional[Path]]:
        """
        Exports validation_report.json and validation_report.md.
        """
        outputs = {}

        # 1. Export JSON
        if self.config.export_json_enabled:
            json_path = self.config.generate_validation_path(f"{file_prefix}.json")
            try:
                json_path.parent.mkdir(parents=True, exist_ok=True)
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(evaluation_result, f, indent=2)
                outputs["json"] = json_path
            except Exception:
                outputs["json"] = None

        # 2. Export Markdown
        if self.config.export_markdown_enabled:
            md_path = self.config.generate_validation_path(f"{file_prefix}.md")
            try:
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_text = self._build_markdown_report(evaluation_result)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
                outputs["markdown"] = md_path
            except Exception:
                outputs["markdown"] = None

        return outputs

    def _build_markdown_report(self, eval_res: Dict[str, Any]) -> str:
        """Constructs GitHub-style Markdown validation report."""
        status = eval_res.get("overall_status", "UNKNOWN")
        score = eval_res.get("readiness_score_pct", 0.0)
        sid = eval_res.get("session_id", "UNKNOWN")
        breakdown = eval_res.get("component_breakdown", {})

        md = []
        md.append(f"# BHID Operational Readiness & Validation Report\n")
        md.append(f"**Target Session**: `{sid}` | **Readiness Score**: `{score:.1f}%` | **Status**: `{status}`\n")
        md.append("---\n")

        if status == "PASSED":
            md.append("> [!TIP]\n> **SYSTEM OPERATIONAL READINESS CONFIRMED**: BHID pipeline passed all consistency, prediction integrity, persistence, replay, and reporting checks.\n")
        else:
            md.append("> [!WARNING]\n> **SYSTEM READINESS ATTENTION REQUIRED**: One or more validation checks failed.\n")

        md.append("## Component Readiness Breakdown\n")
        md.append("| Component Name | Weight | Score | Passed | Weighted Contribution |")
        md.append("|---|---|---|---|---|")

        for comp, data in breakdown.items():
            pass_str = "PASSED" if data.get("passed") else "FAILED"
            md.append(f"| `{comp}` | `{data.get('weight'):.2f}` | `{data.get('score'):.1f}%` | `{pass_str}` | `{data.get('weighted_contribution'):.2f}%` |")

        md.append(f"\n**Composite Readiness Score**: `{score:.1f}%` (Threshold = `{eval_res.get('pass_threshold_pct', 95.0)}%`)\n")
        return "\n".join(md)
