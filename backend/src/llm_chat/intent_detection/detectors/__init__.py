"""
Intent Detectors

Each detector module handles intent detection for a specific app/feature.
"""

from .task_detector import TaskDetector
from .reminder_detector import ReminderDetector

__all__ = ['TaskDetector', 'ReminderDetector']
