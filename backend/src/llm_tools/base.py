"""
Base classes for LLM tools
"""

from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Base class for all LLM tools.
    
    Each tool should inherit from this class and implement the execute method.
    """
    
    # Tool metadata
    name: str = ""
    description: str = ""
    category: str = "general"
    
    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__.lower().replace('tool', '')
        if not self.description:
            raise ValueError(f"Tool {self.name} must have a description")
    
    @abstractmethod
    def execute(self, user, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            user: Django User instance
            **kwargs: Tool-specific parameters
            
        Returns:
            dict: Tool execution result
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's parameter schema.
        
        Returns:
            dict: JSON schema for tool parameters
        """
        return {}
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate tool parameters before execution.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            bool: True if valid
        """
        return True


class ToolFunction:
    """
    Wrapper for function-based tools (simpler than class-based).
    
    This allows defining tools as simple functions with docstrings.
    """
    
    def __init__(
        self,
        func: Callable,
        name: str = None,
        description: str = None,
        category: str = "general",
        parameter_schema: Dict[str, Any] = None
    ):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or ""
        self.category = category
        self.parameter_schema = parameter_schema or {}
    
    def execute(self, user, **kwargs) -> Dict[str, Any]:
        """Execute the wrapped function"""
        try:
            return self.func(user=user, **kwargs)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema"""
        return self.parameter_schema
