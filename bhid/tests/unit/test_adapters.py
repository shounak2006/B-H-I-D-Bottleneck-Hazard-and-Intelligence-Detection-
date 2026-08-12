"""
Unit tests for BHID dataset adapters (MOT20 and MADRAS).
Verifies that schema conversions preserve timestamps, IDs, coordinates, and metadata without data loss.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import unittest
from bhid.dataset.preparation.mot20_adapter import MOT20Adapter
from bhid.dataset.preparation.madras_adapter import MADRASAdapter

class TestAdapters(unittest.TestCase):

    def test_mot20_adapter_parsing(self):
        sample_gt = """
        1, 1, 100.0, 200.0, 50.0, 120.0, 1.0, 1, 0.8, -1
        1, 2, 300.0, 400.0, 45.0, 110.0, 0.9, 1, 0.9, -1
        2, 1, 102.0, 201.0, 50.0, 120.0, 1.0, 1, 0.8, -1
        """
        adapter = MOT20Adapter(sequence_name="MOT20-01Test", fps=25.0)
        frames = adapter.convert_gt_text_to_frames(sample_gt)
        
        self.assertIn(1, frames)
        self.assertIn(2, frames)
        self.assertEqual(len(frames[1].detections), 2)
        self.assertEqual(len(frames[2].detections), 1)
        self.assertEqual(frames[1].detections[0].bbox_xywh, [100.0, 200.0, 50.0, 120.0])
        self.assertEqual(frames[1].timestamp.timestamp_seconds, 0.0)
        self.assertAlmostEqual(frames[2].timestamp.timestamp_seconds, 0.04)

    def test_madras_adapter_parsing(self):
        sample_csv = """
        timestamp_ms, track_id, x_m, y_m, vx_m_s, vy_m_s, density
        1000.0, 101, 12.5, 8.4, 0.5, -0.2, 1.8
        1040.0, 101, 12.7, 8.3, 0.5, -0.2, 1.9
        1080.0, 101, 12.9, 8.2, 0.5, -0.2, 2.0
        """
        adapter = MADRASAdapter(scene_id="scene_test", fps=25.0)
        trajectories = adapter.convert_csv_to_trajectories(sample_csv)
        
        self.assertIn(101, trajectories)
        traj = trajectories[101]
        self.assertEqual(len(traj.states), 3)
        self.assertEqual(traj.states[0].world_pos_xy, [12.5, 8.4])
        self.assertEqual(traj.states[0].velocity_xy, [0.5, -0.2])
        self.assertAlmostEqual(traj.duration_seconds, 0.08, places=4)

if __name__ == "__main__":
    unittest.main()
