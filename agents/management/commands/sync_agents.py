"""
Management command to sync agent definitions to the database.

Usage:
    python manage.py sync_agents
    
This command will create or update agents based on configurations
defined in each app's agents/agent_config.py file.
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from agents.models import Agent
import importlib


class Command(BaseCommand):
    help = 'Sync agent configurations from apps to database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting agent synchronization...'))
        
        # Discover all agent configs from installed apps
        agent_configs = self.discover_agent_configs()
        
        created_count = 0
        updated_count = 0
        
        for config in agent_configs:
            agent, created = Agent.objects.update_or_create(
                name=config['name'],
                defaults={
                    'model_name': config['model_name'],
                    'system_prompt': config['system_prompt'],
                    'max_context_tokens': config['max_context_tokens'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created agent: {agent.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  ↻ Updated agent: {agent.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSync complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
    
    def discover_agent_configs(self):
        """
        Discover agent configurations from all installed apps.
        Looks for {app}/agents/agent_config.py files.
        """
        all_configs = []
        
        # List of apps to check for agent configs
        app_labels = ['chat', 'fitness']  # Add new apps here
        
        for app_label in app_labels:
            try:
                # Try to import the agent_config module
                module_path = f'{app_label}.agents.agent_config'
                module = importlib.import_module(module_path)
                
                # Look for the agent list (convention: {APP}_AGENTS)
                config_var_name = f'{app_label.upper()}_AGENTS'
                
                if hasattr(module, config_var_name):
                    configs = getattr(module, config_var_name)
                    all_configs.extend(configs)
                    self.stdout.write(f'  Found {len(configs)} agent(s) in {app_label}')
                
            except ImportError:
                # App doesn't have agent config, skip it
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error loading {app_label} agents: {e}')
                )
        
        return all_configs
