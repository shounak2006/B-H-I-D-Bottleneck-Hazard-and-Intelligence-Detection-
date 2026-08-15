"""
Unit tests for BHID Trajectory Model (Phase 4C).

Validates:
1. Trajectory point accumulation & history management
2. Temporal duration computation
3. Cumulative Euclidean path length calculation
4. Average velocity vector estimation
5. Recent positions retrieval & serialization
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.vision.tracking.trajectory import Trajectory, TrajectoryPoint


class TestTrajectory(unittest.TestCase):

    def test_initial_empty_trajectory(self):
        traj = Trajectory()
        self.assertEqual(len(traj.points), 0)
        self.assertIsNone(traj.start_time)
        self.assertIsNone(traj.end_time)
        self.assertEqual(traj.duration_seconds(), 0.0)
        self.assertEqual(traj.get_path_length(), 0.0)
        self.assertEqual(traj.get_average_velocity(), (0.0, 0.0))

    def test_add_points_and_path_length(self):
        traj = Trajectory()
        traj.add_point(x=0.0, y=0.0, timestamp=100.0, frame_id=1)
        traj.add_point(x=3.0, y=4.0, timestamp=101.0, frame_id=2)  # distance = 5.0
        traj.add_point(x=6.0, y=8.0, timestamp=102.0, frame_id=3)  # distance = 5.0

        self.assertEqual(len(traj.points), 3)
        self.assertEqual(traj.duration_seconds(), 2.0)
        self.assertAlmostEqual(traj.get_path_length(), 10.0, places=5)

    def test_average_velocity(self):
        traj = Trajectory()
        traj.add_point(x=10.0, y=20.0, timestamp=10.0, frame_id=1)
        traj.add_point(x=30.0, y=60.0, timestamp=12.0, frame_id=3)

        # dt = 2.0s, dx = 20.0, dy = 40.0 -> vx = 10.0, vy = 20.0
        vx, vy = traj.get_average_velocity()
        self.assertAlmostEqual(vx, 10.0, places=5)
        self.assertAlmostEqual(vy, 20.0, places=5)

    def test_max_history_pruning(self):
        traj = Trajectory(max_history_points=5)
        for i in range(10):
            traj.add_point(x=float(i), y=float(i), timestamp=100.0 + i, frame_id=i)

        self.assertEqual(len(traj.points), 5)
        self.assertEqual(traj.points[0].frame_id, 5)
        self.assertEqual(traj.points[-1].frame_id, 9)

    def test_to_dict_serialization(self):
        traj = Trajectory()
        traj.add_point(x=0.0, y=0.0, timestamp=0.0, frame_id=0)
        traj.add_point(x=10.0, y=0.0, timestamp=2.0, frame_id=1)

        d = traj.to_dict()
        self.assertEqual(d["point_count"], 2)
        self.assertEqual(d["duration_seconds"], 2.0)
        self.assertEqual(d["path_length"], 10.0)
        self.assertEqual(d["velocity_x"], 5.0)
        self.assertEqual(d["velocity_y"], 0.0)


if __name__ == "__main__":
    unittest.main()
