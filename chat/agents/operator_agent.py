"""Operator agent for routing user messages to specialist agents"""
from agents.base import BaseAgent
from agents import registry


class OperatorAgent(BaseAgent):
    """
    Routing agent that analyzes user messages and determines 
    which specialist agent should handle them.
    
    This agent doesn't provide direct responses to users,
    instead it routes to appropriate specialists.
    """
    
    def get_system_prompt(self) -> str:
        return self.agent_model.system_prompt
    
    def get_tools(self) -> list:
        # Operator doesn't need tools - just routing logic
        return []


# Register the agent
registry.register('operator', OperatorAgent)
