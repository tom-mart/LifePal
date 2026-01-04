"""Base agent classes"""
import os
from datetime import date
from pydantic_ai import ThinkingPart
from agents.services.llm_service import LLMService
from agents.services.memory_service import MemoryService
from agents.tools import COMMON_TOOLS


class BaseAgent:
    """
    Base class for all specialist agents.
    Override get_system_prompt() and optionally get_tools().
    """
    
    def __init__(self, agent_model):
        """agent_model is the Agent instance from database"""
        self.agent_model = agent_model
    
    def get_system_prompt(self) -> str:
        """Override this to define your agent's behavior"""
        base_prompt = self.agent_model.system_prompt or "You are a helpful assistant."
        
        # Add current date context to help with temporal awareness
        current_date = date.today().strftime('%Y-%m-%d')
        date_context = f"\n\nCurrent date: {current_date}"
        
        return base_prompt + date_context
    
    def get_personalized_system_prompt(self, user) -> str:
        """
        Get system prompt with user-specific personalization injected.
        Use this method when you have user context.
        """
        base_prompt = self.get_system_prompt()
        
        if not user:
            return base_prompt
        
        # Try to get user preferences for this agent
        try:
            from agents.models import UserAgentPreference
            preference = UserAgentPreference.objects.get(user=user, agent=self.agent_model)
            personalization = preference.get_personalization_text()
            
            if personalization:
                # Inject personalization at the start of the prompt
                return f"{personalization}\n\n{base_prompt}"
        except UserAgentPreference.DoesNotExist:
            pass
        
        return base_prompt
    
    def get_tools(self) -> list:
        """
        Override this to provide agent-specific tools.
        Common tools (RAG search) are automatically included.
        Return list of callables.
        """
        return []
    
    def get_all_tools(self) -> list:
        """Get combined list of common tools + agent-specific tools"""
        return COMMON_TOOLS + self.get_tools()
    
    def process_message_stream(self, message: str, conversation, user=None):
        """
        Process a message and return streaming response.
        
        Returns a stream object that can be iterated with stream.stream_text(delta=True).
        After consuming the stream, caller MUST call update_memory() with the stream.
        
        Usage:
            stream = agent.process_message_stream(message, conversation, user)
            for chunk in stream.stream_text(delta=True):
                yield chunk
            # After streaming completes:
            agent.update_memory(conversation, stream)
        """
        # Add user name to context
        full_name = user.get_full_name()
        username = user.username
        if full_name and full_name.strip():
            user_context = f"User Name: {full_name} (Username: {username})"
        else:
            user_context = f"Username: {username}"
        
        # Create LLM service with all tools (common + agent-specific)
        print(f"[AGENT] Creating LLM service for {self.agent_model.name}")
        llm = LLMService(
            model_name=self.agent_model.model_name,
            base_url=os.environ.get("OLLAMA_BASE_URL"),
            system_prompt=self.get_personalized_system_prompt(user),
            max_tokens=self.agent_model.max_context_tokens,
            tools=self.get_all_tools(),
            history_processors=[MemoryService.pruning_processor]
        )
        
        # Chat stream
        print(f"[AGENT] Calling llm.chat_stream()...")
        stream = llm.chat_stream(
            message=message,
            message_history=conversation.short_term_memory,
            context_text=user_context,
            user=user,
            agent=self.agent_model
        )
        print(f"[AGENT] ✓ Stream returned from llm.chat_stream()")
        
        return stream
    
    def update_memory(self, conversation, stream):
        """
        Update conversation memory after streaming completes.
        Call this after consuming all chunks from the stream.
        """
        MemoryService.update_conversation_memory(conversation, stream)
    
    def process_message(self, message: str, conversation, user=None):
        """
        Process a message and return complete response (non-streaming).
        
        Returns tuple: (response_text, reasoning, result_object)
        """
        # Add user name to context
        full_name = user.get_full_name()
        username = user.username
        if full_name and full_name.strip():
            user_context = f"User Name: {full_name} (Username: {username})"
        else:
            user_context = f"Username: {username}"
        
        # Create LLM service
        llm = LLMService(
            model_name=self.agent_model.model_name,
            base_url=os.environ.get("OLLAMA_BASE_URL"),
            system_prompt=self.get_personalized_system_prompt(user),
            max_tokens=self.agent_model.max_context_tokens,
            tools=self.get_all_tools(),
            history_processors=[MemoryService.pruning_processor]
        )
        
        # Get response
        result = llm.chat(
            message=message,
            message_history=conversation.short_term_memory,
            context_text=user_context,
            user=user,
            agent=self.agent_model
        )
        
        # Extract reasoning
        reasoning = None
        for part in result.all_messages()[-1].parts:
            if isinstance(part, ThinkingPart):
                reasoning = part.content
                break
        
        # Update memory
        MemoryService.update_conversation_memory(conversation, result)
        
        return result.output, reasoning, result

