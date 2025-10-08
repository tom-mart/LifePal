"""
Tool Registry

Fully dynamic registry - loads all tools from database.
NO hardcoded tools.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Fully dynamic tool registry.
    All tools loaded from database - NO hardcoded tools.
    """
    
    def __init__(self):
        # No in-memory storage - everything from database
        pass
    
    def get_tool_retriever(self):
        """
        Get the Tool_Retriever as an Ollama Tool.
        This is the ONLY tool initially provided to the LLM.
        """
        from .retriever import TOOL_RETRIEVER_METADATA
        from ollama import Tool
        
        return Tool(
            type='function',
            function=Tool.Function(
                name=TOOL_RETRIEVER_METADATA['name'],
                description=TOOL_RETRIEVER_METADATA['description'],
                parameters=Tool.Function.Parameters(**TOOL_RETRIEVER_METADATA['parameters'])
            )
        )
    
    def get_tools_by_category(self, category: str) -> List:
        """Get tools from database by category"""
        from .models import ToolDefinition
        
        tools = ToolDefinition.objects.filter(
            category=category,
            is_active=True
        )
        
        return [tool.to_ollama_tool() for tool in tools]
    
    def get_all_tools(self) -> List:
        """Get all active tools from database"""
        from .models import ToolDefinition
        
        tools = ToolDefinition.objects.filter(is_active=True)
        return [tool.to_ollama_tool() for tool in tools]
    
    def search_tools(self, query: str) -> List:
        """Search tools by name or description"""
        from django.db.models import Q
        from .models import ToolDefinition
        
        tools = ToolDefinition.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(display_name__icontains=query),
            is_active=True
        )
        
        return [tool.to_ollama_tool() for tool in tools]
    
    def execute_tool(self, tool_name: str, parameters: dict, user) -> dict:
        """
        Execute a tool by name.
        Routes to universal executor which handles all execution types.
        """
        from .models import ToolDefinition
        from .executors import ToolExecutor
        
        # Special handling for Tool_Retriever
        if tool_name == 'tool_retriever':
            from .retriever import tool_retriever
            return tool_retriever(user=user, **parameters)
        
        try:
            tool = ToolDefinition.objects.get(
                name=tool_name,
                is_active=True
            )
        except ToolDefinition.DoesNotExist:
            return {
                'success': False,
                'error': f'Tool {tool_name} not found or inactive'
            }
        
        # Check permissions
        if tool.requires_auth and not user.is_authenticated:
            return {
                'success': False,
                'error': 'Authentication required'
            }
        
        # Execute via universal executor
        return ToolExecutor.execute(tool, parameters, user)
    
    def list_tools(self) -> List[str]:
        """List all active tool names"""
        from .models import ToolDefinition
        
        return list(
            ToolDefinition.objects.filter(is_active=True)
            .values_list('name', flat=True)
        )
    
    def list_categories(self) -> List[str]:
        """List all categories with active tools"""
        from .models import ToolDefinition
        
        return list(
            ToolDefinition.objects.filter(is_active=True)
            .values_list('category', flat=True)
            .distinct()
        )
    
    def get_tools_as_ollama_list(self, category: str = None) -> List:
        """
        Get tools as Ollama Tool list.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of Ollama Tool objects
        """
        from .models import ToolDefinition
        
        if category:
            tools = ToolDefinition.objects.filter(
                category=category,
                is_active=True
            )
        else:
            tools = ToolDefinition.objects.filter(is_active=True)
        
        return [tool.to_ollama_tool() for tool in tools]


# Global registry instance
_registry = None


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry.
    
    Returns:
        ToolRegistry: Global registry instance
    """
    global _registry
    
    if _registry is None:
        _registry = ToolRegistry()
        logger.info("Tool registry initialized (database-driven)")
    
    return _registry
