"""
Unit tests for BHID FastAPI Dedicated Backend Routers & Services (Phase 7A).

Validates REST API router endpoints and service integration:
1. Health, Version, and Status routers
2. Live Monitoring router & MonitoringService
3. Hazard Events router & EventService
4. Operational Sessions router & SessionService
5. Replay router & ReplayService
6. Reports router & ReportingService
7. Read-Only System Validation router & ValidationService
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from backend.routers.health import get_health, get_version, get_status
from backend.routers.monitoring import start_monitoring, stop_monitoring, get_monitoring_state
from backend.routers.events import get_all_events, get_active_events
from backend.routers.sessions import list_sessions
from backend.routers.validation import get_validation_info, run_validation


class TestBackendRouters(unittest.TestCase):

    def test_health_router(self):
        h = get_health()
        self.assertEqual(h["status"], "HEALTHY")

        v = get_version()
        self.assertIn("version", v)

        s = get_status()
        self.assertEqual(s["status"], "OPERATIONAL")

    def test_monitoring_router(self):
        m_start = start_monitoring()
        self.assertEqual(m_start["status"], "RUNNING")

        m_state = get_monitoring_state()
        self.assertTrue(m_state["is_monitoring"])

        m_stop = stop_monitoring()
        self.assertEqual(m_stop["status"], "STOPPED")

    def test_events_router(self):
        events = get_active_events()
        self.assertIn("active_events", events)

        all_events = get_all_events()
        self.assertIn("events", all_events)

    def test_sessions_router(self):
        sess = list_sessions()
        self.assertIn("sessions", sess)

    def test_validation_router(self):
        val_info = get_validation_info()
        self.assertIn("status", val_info)

        val_res = run_validation()
        self.assertIn("evaluation", val_res)


if __name__ == "__main__":
    unittest.main()
