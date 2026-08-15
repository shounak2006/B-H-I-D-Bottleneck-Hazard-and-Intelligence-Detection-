"""
BHID Runtime Pipeline Package.

Provides production runtime architecture connecting live crowd analytics streams
to the trained bottleneck prediction engine developed in Phase 3D.
"""

from bhid.runtime.exceptions import (
    RuntimePipelineError,
    FeatureValidationError,
    WindowNotReadyError,
    PredictionError,
)
from bhid.runtime.feature_schema import (
    FROZEN_FEATURE_NAMES,
    SHORT_TO_CANONICAL_MAP,
    CANONICAL_TO_SHORT_MAP,
    normalize_feature_name,
    normalize_feature_dict,
    validate_feature_dict,
)
from bhid.runtime.feature_window_manager import (
    FeatureWindowManager,
    SampleRecord,
)
from bhid.runtime.pipeline_context import PipelineContext
from bhid.runtime.runtime_prediction_request import RuntimePredictionRequest
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator

__all__ = [
    "RuntimePipelineError",
    "FeatureValidationError",
    "WindowNotReadyError",
    "PredictionError",
    "FROZEN_FEATURE_NAMES",
    "SHORT_TO_CANONICAL_MAP",
    "CANONICAL_TO_SHORT_MAP",
    "normalize_feature_name",
    "normalize_feature_dict",
    "validate_feature_dict",
    "FeatureWindowManager",
    "SampleRecord",
    "PipelineContext",
    "RuntimePredictionRequest",
    "RuntimePredictionResult",
    "RuntimeOrchestrator",
]
