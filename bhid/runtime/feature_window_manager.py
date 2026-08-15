"""
BHID Pure Rolling Temporal Window Manager.

Maintains a 10-second observation window at 2.5Hz cadence (up to 25 samples max).
Acts strictly as a pure sample buffer without mixing analytics/feature computation.
"""

from typing import Dict, Any, List, Optional
from collections import deque
import time
from bhid.runtime.exceptions import FeatureValidationError, WindowNotReadyError
from bhid.runtime.feature_schema import validate_feature_dict


class SampleRecord:
    """Dataclass holding a single timestamped feature snapshot."""
    __slots__ = ("timestamp", "features", "metadata")

    def __init__(self, timestamp: float, features: Dict[str, float], metadata: Optional[Dict[str, Any]] = None):
        self.timestamp = float(timestamp)
        self.features = features
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "features": dict(self.features),
            "metadata": dict(self.metadata)
        }


class FeatureWindowManager:
    """
    Pure rolling temporal window buffer.
    
    Parameters:
        window_duration: Maximum temporal width of observation window in seconds (default: 10.0s).
        cadence_hz: Sample rate cadence in Hz (default: 2.5Hz).
        max_samples: Maximum capacity (default: 25 samples = 10s * 2.5Hz).
    """

    def __init__(
        self,
        window_duration: float = 10.0,
        cadence_hz: float = 2.5,
        max_samples: int = 25
    ):
        self.window_duration = float(window_duration)
        self.cadence_hz = float(cadence_hz)
        self.max_samples = int(max_samples)
        
        self._buffer: deque = deque(maxlen=self.max_samples)
        self._last_timestamp: Optional[float] = None

    @property
    def size(self) -> int:
        """Returns current number of samples in buffer."""
        return len(self._buffer)

    @property
    def capacity(self) -> int:
        """Returns maximum sample capacity of buffer."""
        return self.max_samples

    def is_empty(self) -> bool:
        """Returns True if buffer contains no samples."""
        return len(self._buffer) == 0

    def is_full(self) -> bool:
        """Returns True if buffer has reached maximum capacity (25 samples)."""
        return len(self._buffer) >= self.max_samples

    def is_ready(self, min_samples: int = 1) -> bool:
        """Returns True if buffer has at least min_samples."""
        return len(self._buffer) >= min_samples

    def add_sample(
        self,
        features: Dict[str, Any],
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> SampleRecord:
        """
        Appends a new feature snapshot to the rolling buffer.
        
        Enforces chronological order and automatically purges samples older than window_duration.
        """
        if timestamp is None:
            timestamp = time.time()
        else:
            timestamp = float(timestamp)

        if self._last_timestamp is not None and timestamp < self._last_timestamp:
            raise FeatureValidationError(
                f"Non-chronological timestamp received ({timestamp} < last {self._last_timestamp}). "
                "Future leakage prevention violated."
            )

        if validate:
            validated_features = validate_feature_dict(features)
        else:
            validated_features = {k: float(v) for k, v in features.items()}

        record = SampleRecord(timestamp=timestamp, features=validated_features, metadata=metadata)
        self._buffer.append(record)
        self._last_timestamp = timestamp

        # Evict samples older than window_duration relative to latest timestamp
        self._purge_expired(timestamp)

        return record

    def _purge_expired(self, current_timestamp: float) -> None:
        """Removes samples older than window_duration relative to current_timestamp."""
        cutoff = current_timestamp - self.window_duration
        while self._buffer and self._buffer[0].timestamp < cutoff:
            self._buffer.popleft()

    def get_window_samples(self) -> List[SampleRecord]:
        """Returns all sample records currently in the buffer ordered chronologically."""
        return list(self._buffer)

    def get_latest_sample(self) -> Optional[SampleRecord]:
        """Returns the most recent sample record, or None if buffer is empty."""
        if not self._buffer:
            return None
        return self._buffer[-1]

    def clear(self) -> None:
        """Clears all buffered samples and resets last timestamp."""
        self._buffer.clear()
        self._last_timestamp = None
