from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIModelProfile
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.messages import ModelMessage
from pydantic import TypeAdapter
from typing import Optional, List, Callable
from .tool_parser import TextToolParser
from .deps import AgentDeps


# Models known to not support native tools
MODELS_WITHOUT_TOOL_SUPPORT = [
    'gemma',
    'gemma2',
    'gemma3',
]


class LLMService:
    """Base service for LLM interactions using pydantic-ai"""
    
    def __init__(
        self, 
        model_name: str, 
        base_url: str, 
        system_prompt: str = "", 
        max_tokens: int = 32768,
        tools: Optional[List[Callable]] = None,
        history_processors: Optional[List[Callable]] = None):

        self.model_name = model_name
        self.max_tokens = max_tokens
        self.has_tools = False
        self.base_system_prompt = system_prompt  # Store original prompt
        
        # Check if model supports tools
        supports_tools = not any(model in model_name.lower() for model in MODELS_WITHOUT_TOOL_SUPPORT)
        
        # Configure model profile for models without tool support
        if not supports_tools and tools:
            # Use native structured output mode instead of tool calling
            profile = OpenAIModelProfile(
                default_structured_output_mode='native'
            )
            print(f"⚠️  Model {model_name} doesn't support tools - using native structured output")
        else:
            profile = None
        
        self.ollama_model = OpenAIChatModel(
            model_name=model_name,
            provider=OllamaProvider(base_url=base_url),
            profile=profile,
        )
        
        # Build agent with optional tools and processors
        agent_kwargs = {
            'model': self.ollama_model,
            'system_prompt': system_prompt,
            'deps_type': AgentDeps,
        }
        
        if history_processors:
            agent_kwargs['history_processors'] = history_processors
            
        self.agent = Agent(**agent_kwargs)
        
        # Register tools if provided and model supports them
        self.tools = tools or []
        if tools and supports_tools:
            try:
                for tool in tools:
                    self.agent.tool(tool)
                self.has_tools = True
                print(f"✓ Registered {len(tools)} tool(s) for {model_name}")
            except Exception as e:
                print(f"⚠️  Tool registration failed: {e}")
                self.has_tools = False
        elif tools and not supports_tools:
            # For models without tool support, add tool descriptions to system prompt
            print(f"⚠️  Model {model_name} doesn't support native tools, adding tool descriptions to prompt")
            tool_descriptions = TextToolParser.generate_tool_prompt(tools)
            enhanced_prompt = f"{system_prompt}\n\n{tool_descriptions}"
            
            # Recreate agent with enhanced prompt
            agent_kwargs['system_prompt'] = enhanced_prompt
            self.agent = Agent(**agent_kwargs)
            self.has_tools = False
    
    def _prepare_deps(self, message_history: dict, user, agent=None) -> tuple:
        """Common logic to prepare dependencies and messages"""
        if message_history is None:
            message_history = {"messages": [], "usage": {}}
        
        # Extract messages and usage
        messages_data = message_history.get("messages", [])
        usage = message_history.get("usage", {})
        current_tokens = usage.get("total_tokens", 0)
        
        # Deserialize messages
        if messages_data:
            messages = TypeAdapter(list[ModelMessage]).validate_python(messages_data)
        else:
            messages = []
        
        # Create deps
        deps = AgentDeps(
            max_tokens=self.max_tokens, 
            current_tokens=current_tokens, 
            user=user,
            agent=agent
        )
        
        return deps, messages
    
    def chat(
        self, 
        message: str, 
        message_history: dict = None, 
        context_text: str = None, 
        user=None,
        agent=None):
        """Synchronous chat - returns complete response"""
        
        deps, messages = self._prepare_deps(message_history, user, agent)
        
        # Add context if provided
        if context_text:
            message = f"Context:\n{context_text}\n\nUser Message: {message}"
        
        # Run agent
        response = self.agent.run_sync(
            message, 
            message_history=messages,
            deps=deps,
        )
        
        return response
    
    def chat_stream(
        self, 
        message: str, 
        message_history: dict = None, 
        context_text: str = None, 
        user=None,
        agent=None):
        """Streaming chat - returns stream that can be iterated"""
        
        deps, messages = self._prepare_deps(message_history, user, agent)
        
        # Add context if provided
        if context_text:
            message = f"Context:\n{context_text}\n\nUser Message: {message}"
        
        # For models without native tool support, handle tool calling manually
        if not self.has_tools and self.tools:
            return self._handle_text_tool_calling(message, messages, deps)
        
        # For models with native tool support, use normal streaming
        print(f"[LLM] Starting stream for message: {message[:50]}...")
        print(f"[LLM] Model: {self.model_name}")
        print(f"[LLM] Message history length: {len(messages)}")
        print(f"[LLM] Has tools: {self.has_tools}")
        
        try:
            print(f"[LLM] Calling agent.run_stream_sync()...")
            stream = self.agent.run_stream_sync(
                message,
                message_history=messages,
                deps=deps,
            )
            print(f"[LLM] ✓ Stream object created successfully")
            return stream
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"[ERROR] Stream creation failed")
            print(f"Exception type: {type(e).__module__}.{type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print(f"\nFull traceback:")
            print(f"{'='*80}")
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            print(f"{'='*80}\n")
            raise
    
    def _handle_text_tool_calling(self, message: str, messages: list, deps: AgentDeps):
        """Handle tool calling for models without native tool support"""
        # Get response synchronously to check for tool calls
        response = self.agent.run_sync(
            message,
            message_history=messages,
            deps=deps,
        )
        
        # Parse tool call from response
        parsed = TextToolParser.parse_tool_call(response.output)
        
        if parsed is None:
            # No tool call, just stream the response as-is
            return self.agent.run_stream_sync(
                message,
                message_history=messages,
                deps=deps,
            )
        
        tool_name, kwargs = parsed
        
        # Execute the tool
        tool_result = TextToolParser.execute_tool(tool_name, kwargs, self.tools, deps)
        print(f"🔧 Executed tool: {tool_name}")
        print(f"📊 Result: {tool_result}")
        
        # Create new agent with modified system prompt (tool result + no more tools)
        final_system_prompt = f"""{self.base_system_prompt}

TOOL RESULT:
The tool '{tool_name}' was executed and returned:
{tool_result}

IMPORTANT: You have all the information you need. Answer the user's question directly using the tool result above. 
Do NOT call any more tools."""
        
        # Create temporary agent for final response
        final_agent = Agent(
            model=self.ollama_model,
            system_prompt=final_system_prompt,
            deps_type=AgentDeps,
        )
        
        # Stream the final response
        print(f"🎯 Streaming final response with tool results...")
        return final_agent.run_stream_sync(
            message,
            message_history=messages,
            deps=deps,
        )