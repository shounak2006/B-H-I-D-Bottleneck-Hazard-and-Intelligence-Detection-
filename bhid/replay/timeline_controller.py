"""
BHID Timeline Navigation Controller.

Provides navigation controls (play, pause, stop, seek, next_frame, previous_frame) for replay.
"""

from typing import Optional


class TimelineController:
    """
    Timeline navigation controller managing playback cursor position and state.
    """

    def __init__(self, total_frames: int = 0):
        self.total_frames = max(0, int(total_frames))
        self.current_index: int = 0
        self.is_playing: bool = False

    def play(self) -> None:
        """Sets playback state to playing."""
        self.is_playing = True

    def pause(self) -> None:
        """Sets playback state to paused."""
        self.is_playing = False

    def stop(self) -> None:
        """Stops playback and resets position to start."""
        self.is_playing = False
        self.current_index = 0

    def seek(self, frame_index: int) -> int:
        """Seeks to a specific 0-indexed frame position."""
        if self.total_frames == 0:
            self.current_index = 0
        else:
            self.current_index = max(0, min(int(frame_index), self.total_frames - 1))
        return self.current_index

    def next_frame(self) -> int:
        """Advances playback position by 1 frame."""
        if self.total_frames > 0 and self.current_index < self.total_frames - 1:
            self.current_index += 1
        return self.current_index

    def previous_frame(self) -> int:
        """Rewinds playback position by 1 frame."""
        if self.current_index > 0:
            self.current_index -= 1
        return self.current_index

    def current_frame(self) -> int:
        """Returns current 0-indexed frame position."""
        return self.current_index
