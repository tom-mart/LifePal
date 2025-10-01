"""
Base Handler Class

Provides core functionality for intent handling that all specific handlers inherit from.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HandlerResponse:
    """Response from an intent handler"""
    response_type: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'response_type': self.response_type,
            'message': self.message,
            **self.data
        }


class BaseHandler:
    """
    Base class for intent handlers.
    
    Each app should create its own handler by inheriting from this class
    and implementing the required methods.
    """
    
    # Override in subclasses
    HANDLER_NAME: str = "base"
    SUPPORTED_INTENTS: list = []
    
    def can_handle(self, intent_type: str) -> bool:
        """
        Check if this handler can handle the given intent type.
        
        Args:
            intent_type: Type of intent to check
            
        Returns:
            True if this handler supports the intent type
        """
        return intent_type in self.SUPPORTED_INTENTS
    
    def handle(self, intent_type: str, parameters: Dict[str, Any], user, message) -> Optional[HandlerResponse]:
        """
        Handle an intent and return a response.
        
        Args:
            intent_type: Type of intent to handle
            parameters: Parameters extracted from the message
            user: User who sent the message
            message: Original message object
            
        Returns:
            HandlerResponse or None if intent cannot be handled
        """
        raise NotImplementedError("Subclasses must implement handle()")
    
    def get_supported_intents(self) -> list:
        """Get list of intent types this handler supports"""
        return self.SUPPORTED_INTENTS
