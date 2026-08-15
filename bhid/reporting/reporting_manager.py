"""
BHID Primary Reporting Manager.

Coordinates KPI computation, trend analytics, hazard event intelligence,
cross-session comparative benchmarking, and multi-format report exports.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from bhid.reporting.report_config import ReportConfig
from bhid.reporting.kpi_engine import KPIEngine
from bhid.reporting.trend_analyzer import TrendAnalyzer
from bhid.reporting.event_analytics import EventAnalytics
from bhid.reporting.session_report import SessionReport
from bhid.reporting.comparative_analysis import ComparativeAnalysis
from bhid.reporting.report_generator import ReportGenerator
from bhid.replay.playback_loader import PlaybackLoader


class ReportingManager:
    """
    Primary operational reporting coordinator.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.config.initialize_directories()
        self.generator = ReportGenerator(config=self.config)

    def load_session_data(
        self,
        session_id: str,
        storage_root: Optional[Path] = None
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Loads all persisted Phase 5A session data from disk."""
        loader = PlaybackLoader(session_id=session_id, storage_root=storage_root)
        meta = loader.load_session_metadata()
        preds = loader.load_predictions()
        analytics = loader.load_analytics_snapshots()
        events = loader.load_events()
        return meta, preds, analytics, events

    def generate_report(
        self,
        session_id: str,
        storage_root: Optional[Path] = None,
        export: bool = True
    ) -> SessionReport:
        """
        Generates a complete SessionReport for a historical recording session.
        """
        meta, preds, analytics, events = self.load_session_data(session_id, storage_root)

        kpis = KPIEngine.compute_kpis(predictions=preds, analytics=analytics, events=events)
        trends = TrendAnalyzer.analyze_trends(predictions=preds, analytics=analytics, events=events)
        event_intel = EventAnalytics.analyze_events(events=events)

        report = SessionReport(
            session_id=str(session_id),
            scene_id=str(meta.get("scene_id", "UNKNOWN_SCENE")),
            zone_id=str(meta.get("zone_id", "UNKNOWN_ZONE")),
            reporting_period="ALL",
            kpi_summary=kpis,
            trend_summary=trends,
            event_summary=event_intel
        )

        if export:
            self.export_all(report)

        return report

    def generate_comparative_report(
        self,
        session_ids: List[str],
        storage_root: Optional[Path] = None,
        export: bool = True
    ) -> Dict[str, Any]:
        """
        Generates cross-session comparative benchmarking report across multiple sessions.
        """
        reports = []
        for sid in session_ids:
            rep = self.generate_report(session_id=sid, storage_root=storage_root, export=False)
            reports.append(rep)

        comp_data = ComparativeAnalysis.compare_sessions(reports)

        if export:
            self.generator.generate_comparative_markdown(comp_data)

        return comp_data

    def export_all(self, session_report: SessionReport) -> Dict[str, Optional[Path]]:
        """Flushes session report to JSON, CSV, and Markdown files."""
        return {
            "json": self.generator.export_json(session_report),
            "csv": self.generator.export_csv(session_report),
            "markdown": self.generator.export_markdown(session_report)
        }
