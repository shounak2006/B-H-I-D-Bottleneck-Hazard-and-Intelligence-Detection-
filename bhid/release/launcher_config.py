"""
BHID Windows One-Click Launcher Configuration.

Defines launcher script filenames, backend execution commands, window process titles,
and runtime PID path resolution helpers (`bhid/data/runtime/bhid.pid`).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Optional


@dataclass
class LauncherConfig:
    """
    Central launcher configuration.
    
    Attributes:
        start_bat_filename: Startup batch script filename ("start_bhid.bat").
        stop_bat_filename: Shutdown batch script filename ("stop_bhid.bat").
        backend_cmd: Python CLI execution command for backend service.
        backend_process_title: Dedicated command window title ("BHID_BACKEND_SERVICE").
        pid_file: Path to runtime PID file ("bhid/data/runtime/bhid.pid").
    """
    start_bat_filename: str = "start_bhid.bat"
    stop_bat_filename: str = "stop_bhid.bat"
    backend_cmd: str = "python -m bhid.release.launcher_manager start"
    backend_process_title: str = "BHID_BACKEND_SERVICE"
    pid_file: Path = field(default_factory=lambda: Path("bhid/data/runtime/bhid.pid"))

    def __post_init__(self):
        if isinstance(self.pid_file, str):
            self.pid_file = Path(self.pid_file)

    @staticmethod
    def resolve_project_root() -> Path:
        """Returns root directory path of the BHID workspace."""
        return Path(__file__).resolve().parent.parent.parent

    def get_bat_paths(self, project_root: Optional[Path] = None) -> Tuple[Path, Path]:
        """Returns tuple of (start_bat_path, stop_bat_path) in project root."""
        root = Path(project_root) if project_root else self.resolve_project_root()
        return root / self.start_bat_filename, root / self.stop_bat_filename
