"""
BHID Operational Reporting & Analytics Package.

Provides KPI computation engines, historical trend analyzers, hazard event intelligence,
session report containers, cross-session comparative benchmarking, report generators, and primary reporting managers.
"""

from bhid.reporting.report_config import ReportConfig
from bhid.reporting.kpi_engine import KPIEngine
from bhid.reporting.trend_analyzer import TrendAnalyzer
from bhid.reporting.event_analytics import EventAnalytics
from bhid.reporting.session_report import SessionReport
from bhid.reporting.comparative_analysis import ComparativeAnalysis
from bhid.reporting.report_generator import ReportGenerator
from bhid.reporting.reporting_manager import ReportingManager

__all__ = [
    "ReportConfig",
    "KPIEngine",
    "TrendAnalyzer",
    "EventAnalytics",
    "SessionReport",
    "ComparativeAnalysis",
    "ReportGenerator",
    "ReportingManager",
]
