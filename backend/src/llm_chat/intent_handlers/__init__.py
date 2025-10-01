"""
Intent Handlers Module

This module provides a modular, scalable architecture for handling detected intents.
Each app can register its own handler to process specific intents.
"""

from .base_handler import BaseHandler, HandlerResponse
from .registry import HandlerRegistry, get_handler_registry

__all__ = [
    'BaseHandler',
    'HandlerResponse',
    'HandlerRegistry',
    'get_handler_registry',
]
