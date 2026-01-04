from django.apps import AppConfig


class FitnessConfig(AppConfig):
    name = 'fitness'
    
    def ready(self):
        """Import agents to ensure they register themselves"""
        import fitness.agents.fitness_agent
