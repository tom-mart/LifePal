from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, UserSettings, LLMContextProfile, AIIdentityProfile
import os


class Command(BaseCommand):
    help = 'Create superuser if it does not exist'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'administrator@lifepal.app')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'administrator@lifepal.app')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'insane#4LifePal')
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists')
            )
            return
        
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create related profiles
        UserProfile.objects.create(user=user)
        UserSettings.objects.create(user=user)
        LLMContextProfile.objects.create(user=user)
        AIIdentityProfile.objects.create(user=user)
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" created successfully with all profiles')
        )
