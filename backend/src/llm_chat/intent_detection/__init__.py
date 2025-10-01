"""
Intent Detection Module

This module provides a modular, scalable architecture for detecting user intents
from chat messages. Each app can register its own detector with specific patterns.
"""

from .base_detector import BaseDetector, IntentResult
from .registry import DetectorRegistry, get_detector_registry

__all__ = [
    'BaseDetector',
    'IntentResult',
    'DetectorRegistry',
    'get_detector_registry',
]
