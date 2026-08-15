"""
BHID Runtime Pipeline Exceptions.

Hierarchy:
RuntimePipelineError
 ├── FeatureValidationError
 ├── WindowNotReadyError
 └── PredictionError
"""


class RuntimePipelineError(Exception):
    """Base exception for all BHID runtime errors."""
    pass


class FeatureValidationError(RuntimePipelineError):
    """Raised when input feature dictionary or vector fails schema validation."""
    pass


class WindowNotReadyError(RuntimePipelineError):
    """Raised when attempting operations on an incomplete temporal window buffer."""
    pass


class PredictionError(RuntimePipelineError):
    """Raised when inference engine fails during runtime prediction."""
    pass
