"""
FormAgent - Generic conversational form handler
Collects structured data through natural language interactions
"""
import time
from agents.base import BaseAgent
from agents import registry
from .form_handler import FormHandler


class FormAgent(BaseAgent):
    """
    Generic agent for collecting structured data through conversational forms.
    Can be used for onboarding, surveys, data entry, profile updates, etc.
    
    Flow:
    1. Domain agent detects need for data collection
    2. Domain agent switches conversation to FormAgent with form config
    3. FormAgent collects data through questions
    4. On completion, calls callback and returns to original agent
    """
    
    def _load_form_config(self, conversation):
        """
        Load form configuration from module based on form_type in memory.
        This allows storing just a reference instead of the full config (which has functions).
        """
        form_type = conversation.short_term_memory.get('form_type')
        form_module_path = conversation.short_term_memory.get('form_module')
        
        if not form_type or not form_module_path:
            return None
        
        try:
            # Import the module and get the config
            module = __import__(form_module_path, fromlist=['ONBOARDING_FORM'])
            config = getattr(module, 'ONBOARDING_FORM', None)
            
            if config:
                # Add return_to_agent from memory
                config = config.copy()
                config['return_to_agent'] = conversation.short_term_memory.get('return_to_agent')
                return config
        except Exception as e:
            print(f"[FORM] Error loading form config: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def process_message_stream(self, message: str, conversation, user=None):
        """Override to handle form flow"""
        # Reload conversation to get latest state
        conversation.refresh_from_db()
        
        # Load form config dynamically
        form_config = self._load_form_config(conversation)
        
        if not form_config:
            return self._error_response("No form configuration found")
        
        print(f"[FORM] Processing message for form: {form_config.get('form_type', 'unknown')}")
        
        # Create form handler
        handler = FormHandler(conversation, user, form_config)
        
        # Check if form is active
        if FormHandler.is_active(conversation):
            # Check if this is the first message after activation
            if 'form_state' not in conversation.short_term_memory:
                # Start form flow
                print(f"[FORM] Starting new form")
                response_text = handler.start_form()
            else:
                # Process answer
                print(f"[FORM] Processing answer")
                response_text = handler.process_answer(message)
                
                # Check if form completed and we need to switch back
                if handler.is_complete():
                    # Restore original agent
                    return_to_agent_id = conversation.short_term_memory.get('return_to_agent')
                    if return_to_agent_id:
                        from agents.models import Agent
                        original_agent = Agent.objects.get(id=return_to_agent_id)
                        conversation.agent = original_agent
                        conversation.save(update_fields=['agent'])
                        print(f"[FORM] Form complete - switched back to {original_agent.name}")
        else:
            # Start form
            print(f"[FORM] Activating form")
            response_text = handler.start_form()
        
        # Return a simple stream wrapper
        class FormStream:
            def __init__(self, text):
                self.text = text
                self._timestamp = None
                self.skip_memory_update = True  # Flag to skip LLM memory updates
            
            def stream_text(self, delta=True):
                for char in self.text:
                    yield char
                    time.sleep(0.01)  # 10ms delay between characters for natural streaming effect
            
            def all_messages(self):
                return []
            
            def timestamp(self):
                return self._timestamp
            
            def usage(self):
                """Return mock usage for compatibility"""
                class Usage:
                    input_tokens = 0
                    output_tokens = 0
                    requests = 1
                return Usage()
            
            def all_messages_json(self):
                """Return empty JSON for compatibility"""
                return '[]'
        
        return FormStream(response_text)
    
    def process_message(self, message: str, conversation, user=None):
        """Override to handle form flow (non-streaming)"""
        # Reload conversation to get latest state
        conversation.refresh_from_db()
        
        # Load form config dynamically
        form_config = self._load_form_config(conversation)
        
        if not form_config:
            return "No form configuration found", "[Error]", None
        
        # Create form handler
        handler = FormHandler(conversation, user, form_config)
        
        # Check if form is active
        if FormHandler.is_active(conversation):
            if 'form_state' not in conversation.short_term_memory:
                response_text = handler.start_form()
            else:
                response_text = handler.process_answer(message)
                
                # Check if form completed and we need to switch back
                if handler.is_complete():
                    return_to_agent_id = conversation.short_term_memory.get('return_to_agent')
                    if return_to_agent_id:
                        from agents.models import Agent
                        original_agent = Agent.objects.get(id=return_to_agent_id)
                        conversation.agent = original_agent
                        conversation.save(update_fields=['agent'])
        else:
            response_text = handler.start_form()
        
        return response_text, "[Form]", None
    
    def _error_response(self, error_msg: str):
        """Return an error response stream"""
        class ErrorStream:
            def __init__(self, text):
                self.text = text
                self.skip_memory_update = True  # Flag to skip LLM memory updates
            
            def stream_text(self, delta=True):
                for char in self.text:
                    yield char
                    time.sleep(0.01)  # 10ms delay for natural streaming
            
            def all_messages(self):
                return []
            
            def timestamp(self):
                return None
            
            def usage(self):
                class Usage:
                    input_tokens = 0
                    output_tokens = 0
                    requests = 1
                return Usage()
            
            def all_messages_json(self):
                return '[]'
        
        return ErrorStream(f"❌ Error: {error_msg}")
    
    def get_system_prompt(self) -> str:
        return "You are a form collection agent. You help users fill out forms through conversation."
    
    def get_tools(self) -> list:
        """Form agent doesn't use tools"""
        return []


# Register the agent (matches name transformation: name.lower().replace(' ', '_'))
registry.register('formagent', FormAgent)
