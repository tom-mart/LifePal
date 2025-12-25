from pydantic_ai import RunContext
from pydantic_ai.messages import ModelMessage
from pydantic import TypeAdapter
from typing import List


class MemoryService:
    #Service for managing conversation memory
    
    @staticmethod
    def pruning_processor(ctx: RunContext, messages: List[ModelMessage]) -> List[ModelMessage]:

        # Message processor that prunes memory when token usage is high.
        # Keeps the most recent 20% of messages when threshold is exceeded.

        from agents.services.llm_service import AgentDeps  # Import here to avoid circular
        
        max_tokens = ctx.deps.max_tokens
        current_tokens = ctx.deps.current_tokens
        
        threshold = max_tokens * 0.5
        percentage = (current_tokens / max_tokens) * 100
        
        print(f"DEBUG PRUNING: Current tokens: {current_tokens}/{max_tokens} ({percentage:.1f}%)")
        print(f"DEBUG PRUNING: Threshold: {threshold} (50%)")
        print(f"DEBUG PRUNING: Message count: {len(messages)}")
        
        if current_tokens > threshold:
            keep_count = max(2, int(len(messages) * 0.2))
            print(f"⚠️ PRUNING TRIGGERED! Keeping last {keep_count} of {len(messages)} messages.")
            return messages[-keep_count:]
        else:
            print(f"✓ No pruning needed (under threshold)")
            
        return messages
    
    @staticmethod
    def serialize_messages(messages: List[ModelMessage]) -> dict:
        """Convert messages to JSON-serializable dict"""
        return TypeAdapter(list[ModelMessage]).dump_python(messages, mode='json')
    
    @staticmethod
    def deserialize_messages(messages_data: list) -> List[ModelMessage]:
        """Convert dict back to ModelMessage objects"""
        if messages_data:
            return TypeAdapter(list[ModelMessage]).validate_python(messages_data)
        return []
    
    @staticmethod
    def create_usage_dict(response) -> dict:
        """Extract usage information from response"""
        return {
            "input_tokens": response.usage().input_tokens,
            "output_tokens": response.usage().output_tokens,
            "requests": response.usage().requests,
            "total_tokens": response.usage().input_tokens + response.usage().output_tokens
        }
    
    @staticmethod
    def update_conversation_memory(conversation, response):
        """Update conversation's short-term memory with new messages"""
        all_messages = response.all_messages()
        usage_dict = MemoryService.create_usage_dict(response)
        
        conversation.short_term_memory = {
            "messages": MemoryService.serialize_messages(all_messages),
            "usage": usage_dict
        }
        conversation.save()
        
        print(f"DEBUG: Saved {len(all_messages)} messages to conversation")
        print(f"DEBUG: Total tokens: {usage_dict['total_tokens']} / {conversation.agent.max_context_tokens}")
        print(f"DEBUG: Token usage: {(usage_dict['total_tokens'] / conversation.agent.max_context_tokens) * 100:.1f}%")