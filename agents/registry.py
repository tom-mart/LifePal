"""Agent registry for discovering agent classes"""

# Simple dict to store agent classes
_agents = {}


def register(name: str, agent_class):
    """Register an agent class with a name"""
    if name not in _agents:
        _agents[name] = agent_class
        print(f"✓ Registered agent: {name}")


def get(name: str):
    """Get an agent class by name"""
    return _agents.get(name)


def get_instance(name: str, agent_model):
    """Get an agent instance"""
    agent_class = get(name)
    if not agent_class:
        raise ValueError(f"Agent '{name}' not registered")
    return agent_class(agent_model)


def list_all():
    """List all registered agent names"""
    return list(_agents.keys())
