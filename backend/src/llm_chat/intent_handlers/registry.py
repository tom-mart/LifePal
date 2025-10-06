"""
Handler Registry

Manages registration and discovery of intent handlers.
"""

import logging
from typing import Dict, Any, Optional
from .base_handler import BaseHandler, HandlerResponse

logger = logging.getLogger(__name__)


class HandlerRegistry:
    """Registry for managing intent handlers"""
    
    def __init__(self):
        self._handlers: list[BaseHandler] = []
        self._intent_map: Dict[str, BaseHandler] = {}
    
    def register(self, handler: BaseHandler):
        """
        Register a handler.
        
        Args:
            handler: Handler instance to register
        """
        if handler not in self._handlers:
            self._handlers.append(handler)
            
            # Map intent types to handlers
            for intent_type in handler.get_supported_intents():
                self._intent_map[intent_type] = handler
            
            logger.info(f"Registered handler: {handler.HANDLER_NAME} with intents: {handler.get_supported_intents()}")
    
    def handle_intent(self, intent_type: str, parameters: Dict[str, Any], user, message) -> Optional[HandlerResponse]:
        """
        Handle an intent using the appropriate handler.
        
        Args:
            intent_type: Type of intent to handle
            parameters: Parameters extracted from the message
            user: User who sent the message
            message: Original message object
            
        Returns:
            HandlerResponse or None if no handler found
        """
        handler = self._intent_map.get(intent_type)
        
        if handler:
            try:
                logger.debug(f"Handling intent '{intent_type}' with {handler.HANDLER_NAME}")
                response = handler.handle(intent_type, parameters, user, message)
                if response:
                    logger.info(f"Intent '{intent_type}' handled successfully")
                    return response
            except Exception as e:
                logger.error(f"Error handling intent '{intent_type}': {e}", exc_info=True)
                return HandlerResponse(
                    response_type='error',
                    message="I encountered an error processing your request. Please try again."
                )
        else:
            logger.warning(f"No handler registered for intent type: {intent_type}")
        
        return None
    
    def get_handler_for_intent(self, intent_type: str) -> Optional[BaseHandler]:
        """Get the handler that handles a specific intent type"""
        return self._intent_map.get(intent_type)
    
    def get_all_supported_intents(self) -> list[str]:
        """Get list of all supported intent types across all handlers"""
        return list(self._intent_map.keys())
    
    def auto_discover(self):
        """
        Auto-discover and register all available handlers.
        
        This method imports all handler modules and registers them automatically.
        """
        try:
            from .handlers.task_handler import TaskHandler
            from .handlers.reminder_handler import ReminderHandler

            # List of all available intent handlers
            HANDLERS = [
                TaskHandler,
                ReminderHandler,
            ]
            for handler_class in HANDLERS:
                self.register(handler_class())
            logger.info("Handler auto-discovery complete")
        except ImportError as e:
            logger.warning(f"Could not import some handlers during auto-discovery: {e}")


# Global registry instance
_registry = None


def get_handler_registry() -> HandlerRegistry:
    """Get the global handler registry instance"""
    global _registry
    if _registry is None:
        _registry = HandlerRegistry()
        _registry.auto_discover()
    return _registry
