"""
Management command to seed YouTube download tools into the database.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from llm_tools.models import ToolDefinition, ToolCategory
import os


class Command(BaseCommand):
    help = 'Seed YouTube download tools into the database'

    def handle(self, *args, **options):
        self.stdout.write('Seeding YouTube download tools...')
        
        # Get the base path for scripts
        base_path = os.path.join(settings.BASE_DIR, 'tools', 'scripts')
        
        # Ensure media category exists
        self.create_media_category()
        
        # Create tools
        self.create_youtube_video_tool(base_path)
        self.create_youtube_audio_tool(base_path)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded YouTube tools!'))
    
    def create_media_category(self):
        """Create media category if it doesn't exist"""
        category, created = ToolCategory.objects.get_or_create(
            name='media',
            defaults={
                'display_name': 'Media & Entertainment',
                'description': 'Tools for downloading, processing, and managing media content',
                'icon': '🎵',
                'order': 50
            }
        )
        if created:
            self.stdout.write(f'  Created category: {category.display_name}')
    
    def create_youtube_video_tool(self, base_path):
        """Create the download_youtube_video tool"""
        script_path = os.path.join(base_path, 'download_youtube_video.py')
        
        tool, created = ToolDefinition.objects.get_or_create(
            name='download_youtube_video',
            defaults={
                'display_name': 'Download YouTube Video',
                'category': 'media',
                'description': '''Download video files from YouTube.

Use this tool when the user wants to:
- Download a music video
- Save a YouTube video for offline viewing
- Get a video clip from YouTube
- Download any video content from YouTube

The tool can search YouTube by query or use a direct URL.

Examples:
- "Download the Call on me video by Erik Prydz"
- "Get me the official music video for Bohemian Rhapsody"
- "Download this YouTube video: https://youtube.com/watch?v=..."
- "I want to save the Thriller music video"

The video will be saved to the user's file storage in MP4 format.''',
                'usage_examples': [
                    'User wants to download a music video',
                    'User wants to save a YouTube video',
                    'User provides a YouTube URL to download',
                    'User asks for a specific video clip'
                ],
                'execution_type': 'script',
                'script_path': script_path,
                'script_timeout': 300,  # 5 minutes for large videos
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Search query for YouTube (e.g., "Nothing Else Matters Metallica official video")'
                        },
                        'url': {
                            'type': 'string',
                            'description': 'Direct YouTube URL (optional if query is provided)'
                        }
                    },
                    'required': []
                },
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'file_id': {'type': 'string'},
                        'filename': {'type': 'string'},
                        'title': {'type': 'string'},
                        'download_url': {'type': 'string'},
                        'message': {'type': 'string'}
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
    
    def create_youtube_audio_tool(self, base_path):
        """Create the download_youtube_audio tool"""
        script_path = os.path.join(base_path, 'download_youtube_audio.py')
        
        tool, created = ToolDefinition.objects.get_or_create(
            name='download_youtube_audio',
            defaults={
                'display_name': 'Download YouTube Audio/MP3',
                'category': 'media',
                'description': '''Download audio from YouTube videos and convert to MP3.

Use this tool when the user wants to:
- Download a song as MP3
- Extract audio from a music video
- Get the soundtrack/audio from a YouTube video
- Download music in MP3 format

The tool can search YouTube by query or use a direct URL.
Audio is extracted and converted to high-quality MP3 (192kbps).

Examples:
- "Download Nothing Else Matters by Metallica as MP3"
- "Get me the audio from this video"
- "I want the song Bohemian Rhapsody in MP3 format"
- "Download the soundtrack from this YouTube video"
- "Can you get me Stairway to Heaven as an MP3?"

The MP3 file will be saved to the user's file storage.''',
                'usage_examples': [
                    'User wants to download a song as MP3',
                    'User wants audio from a music video',
                    'User asks for a soundtrack in MP3 format',
                    'User wants to extract audio from YouTube'
                ],
                'execution_type': 'script',
                'script_path': script_path,
                'script_timeout': 300,  # 5 minutes for large files
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Search query for YouTube (e.g., "Nothing Else Matters Metallica")'
                        },
                        'url': {
                            'type': 'string',
                            'description': 'Direct YouTube URL (optional if query is provided)'
                        }
                    },
                    'required': []
                },
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'file_id': {'type': 'string'},
                        'filename': {'type': 'string'},
                        'title': {'type': 'string'},
                        'artist': {'type': 'string'},
                        'download_url': {'type': 'string'},
                        'message': {'type': 'string'}
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
