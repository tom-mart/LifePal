import ollama
import logging
from typing import List, Dict, Any, Optional, Iterator
from django.conf import settings
import json
from django.contrib.auth.models import User
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_DEFAULT_MODEL
        # ollama.Client expects 'host' parameter, not 'base_url'
        self.client = ollama.Client(host=self.base_url, timeout=210)
        
    def is_available(self) -> bool:
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama server not available: {e}")
            return False
        
    def list_models(self) -> List[str]:
        try:
            response = self.client.list()
            if hasattr(response, 'models'):
                return [model.model for model in response.models]
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def chat(self, messages: List[Dict[str, str]], model: str = None, user: User = None) -> str:
        try:
            # Use PromptManager to ensure proper system message with user context
            prompt_manager = PromptManager(user=user)
            messages = prompt_manager.format_chat_messages(
                messages=messages,
                include_user_context=user is not None
            )
            
            response = self.client.chat(
                model=model or self.model,
                messages=messages,
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
            
    def chat_stream(self, messages: List[Dict[str, str]], model: str = None, user: User = None) -> Iterator[str]:
        try:
            # Use PromptManager to ensure proper system message with user context
            prompt_manager = PromptManager(user=user)
            messages = prompt_manager.format_chat_messages(
                messages=messages,
                include_user_context=user is not None
            )
                
            response_stream = self.client.chat(
                model=model or self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in response_stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Ollama streaming chat failed: {e}")
            yield f"\n\nError: Connection to AI service interrupted. {str(e)}"
            raise
    
    def detect_intent(self, message_content: str, user: User = None) -> Dict[str, Any]:
        try:
            # TODO: Implement intent detection prompt in PromptManager
            # For now, return default chat intent
            logger.warning("Intent detection not fully implemented, returning default 'chat' intent")
            return {
                'intent_type': 'chat',
                'confidence': 0.8,
                'parameters': {}
            }
            
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            return {
                'intent_type': 'chat',
                'confidence': 0.1,
                'parameters': {}
            }