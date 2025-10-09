"""
Management command to seed initial tools into the database.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from llm_tools.models import ToolDefinition, ToolCategory
import os


class Command(BaseCommand):
    help = 'Seed initial tools into the database'

    def handle(self, *args, **options):
        self.stdout.write('Seeding tools...')
        
        # Get the base path for scripts
        base_path = os.path.join(settings.BASE_DIR, 'tools', 'scripts')
        
        # Create tool categories
        self.create_categories()
        
        # Create start_checkin tool
        self.create_start_checkin_tool(base_path)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded tools!'))
    
    def create_categories(self):
        """Create tool categories"""
        categories = [
            {
                'name': 'wellbeing',
                'display_name': 'Wellbeing & Check-ins',
                'description': 'Tools for wellbeing tracking, check-ins, and mental health support'
            },
            {
                'name': 'tasks',
                'display_name': 'Task Management',
                'description': 'Tools for managing tasks, todos, and productivity'
            },
            {
                'name': 'reminders',
                'display_name': 'Reminders',
                'description': 'Tools for creating and managing reminders and notifications'
            },
            {
                'name': 'moments',
                'display_name': 'Moments & Journaling',
                'description': 'Tools for capturing moments, journaling, and reflection'
            },
            {
                'name': 'communication',
                'display_name': 'Communication',
                'description': 'Tools for communication, messaging, and social interactions'
            },
            {
                'name': 'information',
                'display_name': 'Information Retrieval',
                'description': 'Tools for retrieving, searching, and processing information'
            },
        ]
        
        for cat_data in categories:
            category, created = ToolCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created category: {category.display_name}')
    
    def create_start_checkin_tool(self, base_path):
        """Create the start_checkin tool"""
        script_path = os.path.join(base_path, 'start_checkin.py')
        
        tool, created = ToolDefinition.objects.get_or_create(
            name='start_checkin',
            defaults={
                'display_name': 'Start Check-in',
                'category': 'wellbeing',
                'description': '''Start a wellbeing check-in conversation.

Use this tool when the user wants to:
- Start their morning check-in
- Do a midday check-in
- Start their evening reflection
- Do an ad-hoc check-in
- Talk about how they're feeling

This tool creates a check-in record and gathers relevant context like today's tasks and previous check-ins.

Examples:
- "I want to start my morning check-in"
- "Let's do my evening reflection"
- "I need to check in"
- "I want to talk about how I'm feeling"''',
                'usage_examples': [
                    'User wants to start morning check-in',
                    'User wants to do evening reflection',
                    'User wants to talk about feelings'
                ],
                'execution_type': 'script',
                'script_path': script_path,
                'script_timeout': 30,
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'checkin_type': {
                            'type': 'string',
                            'enum': ['morning', 'midday', 'evening', 'adhoc'],
                            'description': 'Type of check-in (morning, midday, evening, or adhoc)'
                        },
                        'reason': {
                            'type': 'string',
                            'description': 'Optional reason for the check-in'
                        }
                    },
                    'required': []
                },
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'checkin_id': {'type': 'string'},
                        'context': {'type': 'object'},
                        'suggestions': {'type': 'array'}
                    }
                },
                'is_active': True,
                'requires_auth': True,
                'version': '1.0'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  Created tool: {tool.name}'))
        else:
            self.stdout.write(f'  Tool already exists: {tool.name}')
