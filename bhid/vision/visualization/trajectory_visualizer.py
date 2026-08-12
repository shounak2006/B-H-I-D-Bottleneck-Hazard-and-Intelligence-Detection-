"""
Trajectory Diagnostic Rendering Engine for BHID.
Exclusively reserved for rendering trajectory overlays, density heatmap diagnostics,
and trajectory continuity plots.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from typing import Dict, Any
from bhid.vision.tracking.trajectory_generator import TrajectoryGenerator, Trajectory, Track

class TrajectoryVisualizer:
    """Diagnostic rendering engine for trajectory streams."""

    @staticmethod
    def generate_ascii_heatmap(density_grid: list, width: int = 5, height: int = 5) -> str:
        """Generates an ASCII visualization of density grid for console inspection."""
        chars = [".", ":", "-", "=", "+", "*", "#", "%", "@"]
        lines = []
        for r in range(height):
            row_str = ""
            for c in range(width):
                val = density_grid[r][c] if r < len(density_grid) and c < len(density_grid[r]) else 0.0
                idx = min(int(val), len(chars) - 1)
                row_str += chars[idx] * 2
            lines.append(row_str)
        return "\n".join(lines)

def main():
    print("--- Diagnostic Rendering Engine Initialized ---")
    grid = [[0, 1, 2], [1, 3, 4], [0, 2, 1]]
    print(TrajectoryVisualizer.generate_ascii_heatmap(grid, 3, 3))

if __name__ == "__main__":
    main()
