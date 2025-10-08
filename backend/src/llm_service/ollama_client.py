import ollama
import logging
from typing import List, Dict, Any, Optional, Iterator, Union
from django.conf import settings
import json
from django.contrib.auth.models import User
from .prompt_manager import PromptManager
from ollama import Tool

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

    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None, 
        user: User = None,
        use_tools: bool = True,
        max_iterations: int = 10
    ) -> str:
        """
        Chat with automatic tool calling support using Tool_Retriever pattern.
        
        Args:
            messages: Conversation messages
            model: Model to use
            user: User context for tool execution
            use_tools: Whether to enable Tool_Retriever pattern
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Final assistant message content
        """
        try:
            # Use PromptManager to ensure proper system message with user context
            prompt_manager = PromptManager(user=user)
            current_messages = prompt_manager.format_chat_messages(
                messages=messages,
                include_user_context=user is not None
            )
            
            # Get Tool_Retriever if tools are enabled
            tools = None
            if use_tools:
                from llm_tools import get_tool_registry
                registry = get_tool_registry()
                tools = [registry.get_tool_retriever()]
            
            iterations = 0
            discovered_tools = {}  # Cache discovered tools
            
            while iterations < max_iterations:
                # Call LLM
                response = self.client.chat(
                    model=model or self.model,
                    messages=current_messages,
                    tools=tools,
                    stream=False
                )
                
                message = response['message']
                
                # Check for tool calls
                if not use_tools or not message.get('tool_calls'):
                    # No tool calls, return content
                    return message.get('content', '')
                
                # Add assistant message with tool calls
                current_messages.append(message)
                
                # Execute each tool call
                for tool_call in message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_params = tool_call['function']['arguments']
                    
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Execute tool
                    from llm_tools import get_tool_registry
                    registry = get_tool_registry()
                    result = registry.execute_tool(tool_name, tool_params, user)
                    
                    # If Tool_Retriever was called, inject discovered tools
                    if tool_name == 'tool_retriever' and result.get('success'):
                        # Get the actual tool objects
                        category = tool_params.get('intent_category')
                        query = tool_params.get('query')
                        
                        if category:
                            new_tools = registry.get_tools_as_ollama_list(category)
                        elif query:
                            tool_objs = registry.search_tools(query)
                            new_tools = [registry.get_tool_schema(t.name) for t in tool_objs]
                        else:
                            new_tools = registry.get_tools_as_ollama_list()
                        
                        # Add discovered tools to available tools
                        if tools is None:
                            tools = []
                        tools.extend(new_tools)
                        
                        logger.info(f"Discovered {len(new_tools)} tools, total available: {len(tools)}")
                    
                    # Add tool result message
                    current_messages.append({
                        'role': 'tool',
                        'content': json.dumps(result),
                    })
                
                iterations += 1
            
            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached in tool calling")
            return "I apologize, but I'm having trouble completing that request."
            
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}", exc_info=True)
            raise
            
    def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None, 
        user: User = None,
        use_tools: bool = True,
        max_iterations: int = 10
    ) -> Iterator[Union[str, Dict]]:
        """
        Streaming chat with Tool_Retriever pattern support.
        
        Args:
            messages: Conversation messages
            model: Model to use
            user: User context for tool execution
            use_tools: Whether to enable Tool_Retriever pattern
            max_iterations: Maximum tool calling iterations
            
        Yields:
            - str: Content chunks
            - dict: Tool events with type='tool_call', 'tool_result', or 'tools_discovered'
        """
        try:
            # Use PromptManager to ensure proper system message with user context
            prompt_manager = PromptManager(user=user)
            current_messages = prompt_manager.format_chat_messages(
                messages=messages,
                include_user_context=user is not None
            )
            
            # Get Tool_Retriever if tools are enabled
            tools = None
            if use_tools:
                from llm_tools import get_tool_registry
                registry = get_tool_registry()
                tools = [registry.get_tool_retriever()]
            
            iterations = 0
            
            while iterations < max_iterations:
                response_stream = self.client.chat(
                    model=model or self.model,
                    messages=current_messages,
                    tools=tools,
                    stream=True
                )
                
                full_message = {'role': 'assistant', 'content': '', 'tool_calls': []}
                
                # Stream content
                for chunk in response_stream:
                    message = chunk.get('message', {})
                    
                    # Stream content
                    if content := message.get('content'):
                        full_message['content'] += content
                        yield content
                    
                    # Collect tool calls
                    if tool_calls := message.get('tool_calls'):
                        full_message['tool_calls'].extend(tool_calls)
                
                # Check if we have tool calls
                if not use_tools or not full_message.get('tool_calls'):
                    break
                
                # Add assistant message
                current_messages.append(full_message)
                
                # Execute tools
                for tool_call in full_message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_params = tool_call['function']['arguments']
                    
                    # Yield tool call event
                    yield {
                        'type': 'tool_call',
                        'name': tool_name,
                        'parameters': tool_params
                    }
                    
                    # Execute tool
                    from llm_tools import get_tool_registry
                    registry = get_tool_registry()
                    result = registry.execute_tool(tool_name, tool_params, user)
                    
                    # If Tool_Retriever was called, inject discovered tools
                    if tool_name == 'tool_retriever' and result.get('success'):
                        category = tool_params.get('intent_category')
                        query = tool_params.get('query')
                        
                        if category:
                            new_tools = registry.get_tools_as_ollama_list(category)
                        elif query:
                            tool_objs = registry.search_tools(query)
                            new_tools = [registry.get_tool_schema(t.name) for t in tool_objs]
                        else:
                            new_tools = registry.get_tools_as_ollama_list()
                        
                        # Add discovered tools
                        if tools is None:
                            tools = []
                        tools.extend(new_tools)
                        
                        # Yield tools discovered event
                        yield {
                            'type': 'tools_discovered',
                            'count': len(new_tools),
                            'tools': [t.function.name for t in new_tools]
                        }
                    
                    # Yield tool result event
                    yield {
                        'type': 'tool_result',
                        'name': tool_name,
                        'result': result
                    }
                    
                    # Add tool result to messages
                    current_messages.append({
                        'role': 'tool',
                        'content': json.dumps(result),
                    })
                
                iterations += 1
            
            if iterations >= max_iterations:
                logger.warning(f"Max iterations ({max_iterations}) reached in streaming")
                    
        except Exception as e:
            logger.error(f"Ollama streaming chat failed: {e}", exc_info=True)
            yield f"\n\nError: Connection to AI service interrupted. {str(e)}"
            raise