"""
Tool_Retriever - Meta-tool for dynamic tool discovery

This is the only tool initially provided to the LLM. It returns
available tools based on context, following the ReAct pattern.
"""

from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def tool_retriever(
    user,
    intent_category: Optional[str] = None,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve available tools for the current context.
    
    Call this function whenever you need to perform an action, fetch data,
    or interact with external systems. It will return the appropriate tools
    you can use to fulfill the user's request.
    
    Args:
        user: User context (automatically provided)
        intent_category: Optional category hint. Options:
            - 'wellbeing': Check-in and wellbeing tools
            - 'tasks': Task management tools
            - 'reminders': Reminder tools
            - 'moments': Moment capture tools
            - 'context': Context retrieval tools
        query: Optional natural language query describing what you need to do
        
    Returns:
        dict: Available tools with their definitions, parameters, and usage examples
        
    Examples:
        - tool_retriever(intent_category='wellbeing') → Returns check-in tools
        - tool_retriever(intent_category='tasks') → Returns task management tools
        - tool_retriever(query='start a check-in') → Returns relevant tools
        - tool_retriever() → Returns all available tools
    """
    from .registry import get_tool_registry
    
    registry = get_tool_registry()
    
    try:
        # Get ToolDefinition models (not Ollama Tool objects)
        from .models import ToolDefinition
        from django.db.models import Q
        
        if intent_category:
            # Get tools by category
            tools = ToolDefinition.objects.filter(
                category=intent_category,
                is_active=True
            )
            logger.info(f"Tool_Retriever: Retrieved {tools.count()} tools for category '{intent_category}'")
        elif query:
            # Search tools by query
            tools = ToolDefinition.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(display_name__icontains=query),
                is_active=True
            )
            logger.info(f"Tool_Retriever: Found {tools.count()} tools matching query '{query}'")
        else:
            # Return all available tools
            tools = ToolDefinition.objects.filter(is_active=True)
            logger.info(f"Tool_Retriever: Retrieved all {tools.count()} available tools")
        
        # Format tools for LLM consumption
        tool_definitions = []
        for tool in tools:
            tool_def = {
                'name': tool.name,
                'description': tool.description,
                'category': tool.category,
                'parameters': tool.parameters_schema
            }
            tool_definitions.append(tool_def)
        
        return {
            'success': True,
            'tools_count': len(tool_definitions),
            'tools': tool_definitions,
            'message': f"Retrieved {len(tool_definitions)} tools" + 
                      (f" for category '{intent_category}'" if intent_category else "")
        }
    
    except Exception as e:
        logger.error(f"Tool_Retriever error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'tools': []
        }


# Tool metadata for Tool_Retriever itself
TOOL_RETRIEVER_METADATA = {
    'name': 'tool_retriever',
    'description': (
        'Retrieve available tools for performing actions or fetching data. '
        'Call this FIRST when you need to interact with external systems, '
        'create/modify data, or fetch information. '
        'Returns tool definitions you can then use.'
    ),
    'category': 'meta',
    'parameters': {
        'type': 'object',
        'properties': {
            'intent_category': {
                'type': 'string',
                'enum': ['wellbeing', 'tasks', 'reminders', 'moments', 'context'],
                'description': 'Category of tools needed (optional but recommended for efficiency)'
            },
            'query': {
                'type': 'string',
                'description': 'Natural language description of what you need to do (optional)'
            }
        },
        'required': []
    },
    'examples': [
        {
            'scenario': 'User wants to start a check-in',
            'call': "tool_retriever(intent_category='wellbeing')",
            'result': 'Returns check-in related tools'
        },
        {
            'scenario': 'User wants to create a task',
            'call': "tool_retriever(intent_category='tasks')",
            'result': 'Returns task management tools'
        },
        {
            'scenario': 'Not sure which tools are needed',
            'call': "tool_retriever(query='help user track their mood')",
            'result': 'Returns relevant tools based on semantic search'
        }
    ]
}
