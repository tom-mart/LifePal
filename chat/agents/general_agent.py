"""General purpose agent for non-specialized queries"""
from agents.base import BaseAgent
from agents import registry


class GeneralAgent(BaseAgent):
    """
    General purpose agent that handles:
    - General questions
    - Casual conversation
    - Explanations
    - Anything not covered by specialist agents
    """
    
    def get_system_prompt(self) -> str:
        return self.agent_model.system_prompt
    
    def get_tools(self) -> list:
        # No special tools, just conversation
        return []


# Register the agent
registry.register('general_agent', GeneralAgent)
