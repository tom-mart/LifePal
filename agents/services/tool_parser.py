"""Helper service for text-based tool calling in models without native tool support"""
import re
import inspect
from typing import Callable, List, Optional, Tuple
from types import SimpleNamespace


class TextToolParser:
    """Parse and execute tools from text-based responses"""
    
    @staticmethod
    def generate_tool_prompt(tools: List[Callable]) -> str:
        """Generate tool descriptions for text-based tool calling"""
        if not tools:
            return ""
        
        tool_docs = [
            "\n=== AVAILABLE TOOLS ===",
            "You have access to the following tools. When you need to use a tool, respond with ONLY the tool call in this exact format:",
            "TOOL_CALL: tool_name(arg='value')",
            "",
            "After calling a tool, I will provide you with the result, and you should then respond to the user based on that result.",
            ""
        ]
        
        for tool in tools:
            tool_name = tool.__name__
            tool_doc = tool.__doc__ or "No description"
            
            # Get function signature
            try:
                sig = inspect.signature(tool)
                params = []
                for param_name, param in sig.parameters.items():
                    if param_name == 'ctx':  # Skip RunContext
                        continue
                    param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
                    params.append(f"{param_name}: {param_type}")
                
                tool_docs.append(f"Tool: {tool_name}({', '.join(params)})")
                tool_docs.append(f"  {tool_doc.strip()}")
                tool_docs.append("")
            except Exception:
                tool_docs.append(f"Tool: {tool_name}()")
                tool_docs.append(f"  {tool_doc.strip()}")
                tool_docs.append("")
        
        tool_docs.append("IMPORTANT: When you need to call a tool, respond with ONLY: TOOL_CALL: tool_name(arg='value')")
        tool_docs.append("Do not include any other text before or after the tool call.")
        tool_docs.append("=== END TOOLS ===\n")
        
        return "\n".join(tool_docs)
    
    @staticmethod
    def parse_tool_call(text: str) -> Optional[Tuple[str, dict]]:
        """
        Parse a tool call from text.
        Returns (tool_name, kwargs) or None if no valid tool call found.
        """
        # Match TOOL_CALL: function_name(args)
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text)
        
        if not match:
            return None
        
        tool_name = match.group(1)
        args_str = match.group(2)
        
        # Parse arguments
        kwargs = {}
        if args_str.strip():
            # Handle both arg='value' and arg="value"
            arg_pattern = r"(\w+)=(['\"])(.*?)\2"
            for arg_match in re.finditer(arg_pattern, args_str):
                key = arg_match.group(1)
                value = arg_match.group(3)
                kwargs[key] = value
            
            # Also handle numeric arguments without quotes
            num_pattern = r"(\w+)=([0-9.]+)"
            for arg_match in re.finditer(num_pattern, args_str):
                key = arg_match.group(1)
                value = arg_match.group(2)
                # Try to convert to appropriate type
                try:
                    kwargs[key] = int(value)
                except ValueError:
                    try:
                        kwargs[key] = float(value)
                    except ValueError:
                        kwargs[key] = value
        
        return tool_name, kwargs
    
    @staticmethod
    def execute_tool(tool_name: str, kwargs: dict, tools: List[Callable], deps) -> str:
        """Execute a tool by name with given arguments"""
        # Find the tool function
        tool_func = None
        for tool in tools:
            if tool.__name__ == tool_name:
                tool_func = tool
                break
        
        if not tool_func:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            # Create a mock RunContext
            ctx = SimpleNamespace(deps=deps)
            
            # Execute the tool
            result = tool_func(ctx, **kwargs)
            return result
            
        except Exception as e:
            return f"Error executing tool: {str(e)}"
