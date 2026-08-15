"""
BHID Session Report Data Model & Markdown Generator.

Dataclass container holding complete session report metrics, trend summaries,
event intelligence, and formatting GitHub-style Markdown operational reports.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class SessionReport:
    """
    Structured operational session report container.
    """
    session_id: str
    scene_id: str = "UNKNOWN_SCENE"
    zone_id: str = "UNKNOWN_ZONE"
    reporting_period: str = "ALL"
    kpi_summary: Dict[str, Any] = field(default_factory=dict)
    trend_summary: Dict[str, Any] = field(default_factory=dict)
    event_summary: Dict[str, Any] = field(default_factory=dict)
    generated_timestamp: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "session_id": self.session_id,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "reporting_period": self.reporting_period,
            "generated_timestamp": self.generated_timestamp,
            "kpi_summary": dict(self.kpi_summary),
            "trend_summary": dict(self.trend_summary),
            "event_summary": dict(self.event_summary)
        }

    def to_markdown(self) -> str:
        """
        Generates GitHub-style Markdown operational intelligence report.
        """
        kpis = self.kpi_summary
        evts = self.event_summary.get("summary", {})
        durations = self.event_summary.get("durations", {})
        rankings = self.event_summary.get("zone_rankings", [])
        risk_dist = self.trend_summary.get("risk_distribution", {})

        md = []
        md.append(f"# BHID Operational Intelligence Report - Session `{self.session_id}`\n")
        md.append(f"**Scene ID**: `{self.scene_id}` | **Zone ID**: `{self.zone_id}` | **Reporting Window**: `{self.reporting_period}`\n")
        md.append("---\n")

        # Alerts callouts
        peak_prob = kpis.get("peak_prediction_probability", 0.0)
        tot_events = kpis.get("total_hazard_events", 0)

        if peak_prob >= 0.85:
            md.append("> [!CAUTION]\n> **CRITICAL HAZARD OBSERVED**: Bottleneck risk probability reached **{:.1f}%**. Sustained crowding recorded.\n".format(peak_prob * 100.0))
        elif peak_prob >= 0.60:
            md.append("> [!WARNING]\n> **HIGH BOTTLENECK HAZARD DETECTED**: Bottleneck risk probability reached **{:.1f}%**.\n".format(peak_prob * 100.0))
        else:
            md.append("> [!NOTE]\n> **NORMAL OPERATIONAL PARAMETERS**: Flow density remained within safe operational thresholds.\n")

        # KPI Summary Table
        md.append("## Operational Key Performance Indicators (KPIs)\n")
        md.append("| Metric Name | Value | Unit / Status |")
        md.append("|---|---|---|")
        md.append(f"| **Peak Pedestrian Count** | `{kpis.get('peak_pedestrian_count', 0)}` | Pedestrians |")
        md.append(f"| **Average Pedestrian Count** | `{kpis.get('average_pedestrian_count', 0.0)}` | Pedestrians |")
        md.append(f"| **Peak Crowd Density** | `{kpis.get('peak_density_ped_per_m2', 0.0)}` | ped/m² |")
        md.append(f"| **Average Crowd Density** | `{kpis.get('average_density_ped_per_m2', 0.0)}` | ped/m² |")
        md.append(f"| **Peak Risk Probability (Y30)** | `{kpis.get('peak_prediction_probability', 0.0)*100:.1f}%` | Threshold = 60% |")
        md.append(f"| **Total Hazard Events** | `{kpis.get('total_hazard_events', 0)}` | Events |")
        md.append(f"| **Event Resolution Rate** | `{kpis.get('resolution_rate_pct', 100.0):.1f}%` | Target = 100% |")
        md.append(f"| **Average Event Duration** | `{kpis.get('average_event_duration_seconds', 0.0)}s` | Seconds |\n")

        # Risk Distribution Table
        md.append("## Bottleneck Risk Distribution\n")
        md.append("| Risk Level | Classification | Sample Count |")
        md.append("|---|---|---|")
        md.append(f"| **LOW** | Probability < 30% | `{risk_dist.get('LOW', 0)}` |")
        md.append(f"| **MODERATE** | 30% <= Probability < 60% | `{risk_dist.get('MODERATE', 0)}` |")
        md.append(f"| **HIGH** | 60% <= Probability < 85% | `{risk_dist.get('HIGH', 0)}` |")
        md.append(f"| **CRITICAL** | Probability >= 85% | `{risk_dist.get('CRITICAL', 0)}` |\n")

        # Hazard Event Intelligence
        md.append("## Hazard Event Intelligence\n")
        md.append(f"- **Total Events Recorded**: `{evts.get('total_events', 0)}`")
        md.append(f"- **Resolved Events**: `{evts.get('resolved_events', 0)}`")
        md.append(f"- **Max Duration Single Event**: `{durations.get('max_duration_seconds', 0.0)}s`\n")

        if rankings:
            md.append("### Spatial Zone Risk Rankings\n")
            md.append("| Rank | Zone ID | Scene ID | Event Count | Critical Events | Max Risk Prob |")
            md.append("|---|---|---|---|---|---|")
            for idx, r in enumerate(rankings, 1):
                md.append(f"| {idx} | `{r.get('zone_id')}` | `{r.get('scene_id')}` | `{r.get('event_count')}` | `{r.get('critical_count')}` | `{r.get('max_probability')*100:.1f}%` |")
            md.append("\n")

        return "\n".join(md)
