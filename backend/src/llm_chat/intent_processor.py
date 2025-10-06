"""
Intent Processor

Main entry point for intent detection and handling.
Coordinates between detectors and handlers.
"""

import logging
from typing import Dict, Any, Optional
from .models import Message, Intent
from .intent_detection import get_detector_registry
from .intent_handlers import get_handler_registry

logger = logging.getLogger(__name__)


class IntentProcessor:
    """
    Main processor for detecting and handling intents.
    
    This class coordinates between the detection and handling systems,
    providing a simple interface for the API layer.
    """
    
    def __init__(self):
        self.detector_registry = get_detector_registry()
        self.handler_registry = get_handler_registry()
    
    def process_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Process a message: detect intent and handle it.
        
        Args:
            message: Message object to process
            
        Returns:
            Response dictionary or None if no intent handling needed
        """
        # Only process user messages
        if message.role != 'user':
            return None
        
        # Build context from conversation
        context = self._build_context(message)
        
        # Detect intent
        intent_result = self.detector_registry.detect_intent(message.content, context)
        
        if not intent_result:
            return None
        
        # Skip 'chat' intent - it's just a fallback for normal conversation
        if intent_result.intent_type == 'chat':
            return None
        
        # Create Intent record
        intent = Intent.objects.create(
            message=message,
            intent_type=intent_result.intent_type,
            confidence=intent_result.confidence,
            parameters=intent_result.parameters,
            processed=False
        )
        
        logger.info(f"Detected intent: {intent.intent_type} (confidence: {intent.confidence})")
        
        # Handle intent if confidence is high enough
        if intent.confidence > 0.3:
            response = self.handler_registry.handle_intent(
                intent_type=intent.intent_type,
                parameters=intent.parameters,
                user=message.conversation.user,
                message=message
            )
            
            if response:
                # Mark intent as processed
                intent.processed = True
                intent.save()
                
                # Return response as dictionary
                return response.to_dict()
        
        return None
    
    def _build_context(self, message: Message) -> Dict[str, Any]:
        """
        Build conversation context for intent detection.
        
        Args:
            message: Current message
            
        Returns:
            Context dictionary with recent messages and intents
        """
        conversation = message.conversation
        recent_messages = list(
            conversation.messages
            .order_by('-created_at')[:6]
            .values('id', 'role', 'content', 'created_at')
        )
        
        # Add intent information to messages
        for msg in recent_messages:
            try:
                intent = Intent.objects.filter(message_id=msg['id']).first()
                if intent:
                    msg['intent'] = {
                        'id': str(intent.id),
                        'intent_type': intent.intent_type,
                        'confidence': intent.confidence,
                        'parameters': intent.parameters
                    }
            except Intent.DoesNotExist:
                pass
        
        return {
            'recent_messages': recent_messages,
            'conversation_id': str(conversation.id)
        }
    
    def get_supported_intents(self) -> Dict[str, list]:
        """
        Get all supported intents organized by category.
        
        Returns:
            Dictionary mapping categories to intent lists
        """
        return {
            'detectors': self.detector_registry.get_all_supported_intents(),
            'handlers': self.handler_registry.get_all_supported_intents()
        }
