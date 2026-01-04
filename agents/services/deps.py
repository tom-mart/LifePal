"""
Shared dependencies for agent services.
Separated to avoid circular imports between llm_service and memory_service.
"""


class AgentDeps:
    """Dependencies passed to all agents during execution"""
    def __init__(self, max_tokens: int, current_tokens: int, user=None, agent=None):
        self.max_tokens = max_tokens
        self.current_tokens = current_tokens
        self.user = user
        self.agent = agent
