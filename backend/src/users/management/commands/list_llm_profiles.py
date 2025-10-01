from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import LLMContextProfile


class Command(BaseCommand):
    help = 'List all LLMContextProfile records with their associated users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== All LLMContextProfile Records ===\n'))
        
        profiles = LLMContextProfile.objects.all().select_related('user')
        
        if not profiles:
            self.stdout.write(self.style.WARNING('No LLMContextProfile records found.'))
            return
        
        for profile in profiles:
            self.stdout.write(f"\nProfile ID: {profile.id}")
            self.stdout.write(f"  User ID: {profile.user.id}")
            self.stdout.write(f"  Username: {profile.user.username}")
            self.stdout.write(f"  Email: {profile.user.email}")
            self.stdout.write(f"  Created: {profile.created_at}")
            self.stdout.write(f"  Updated: {profile.updated_at}")
            self.stdout.write("-" * 50)
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal profiles: {profiles.count()}'))
        
        # Check for users without profiles
        self.stdout.write(self.style.SUCCESS('\n=== Users Without LLMContextProfile ===\n'))
        users_without_profile = User.objects.filter(llmcontextprofile__isnull=True)
        
        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users have LLMContextProfile records.'))
        else:
            for user in users_without_profile:
                self.stdout.write(f"  User ID: {user.id}, Username: {user.username}, Email: {user.email}")
            self.stdout.write(self.style.WARNING(f'\nTotal users without profile: {users_without_profile.count()}'))
