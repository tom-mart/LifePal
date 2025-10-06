from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, UserSettings, LLMContextProfile, AIIdentityProfile


class Command(BaseCommand):
    help = 'Create missing profiles for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        
        for user in users:
            created_profiles = []
            
            # Create UserProfile if missing
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                created_profiles.append('UserProfile')
            
            # Create UserSettings if missing
            if not hasattr(user, 'usersettings'):
                UserSettings.objects.create(user=user)
                created_profiles.append('UserSettings')
            
            # Create LLMContextProfile if missing
            if not hasattr(user, 'llm_context'):
                LLMContextProfile.objects.create(user=user)
                created_profiles.append('LLMContextProfile')
            
            # Create AIIdentityProfile if missing
            if not hasattr(user, 'ai_identity'):
                AIIdentityProfile.objects.create(user=user)
                created_profiles.append('AIIdentityProfile')
            
            if created_profiles:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {", ".join(created_profiles)} for user: {user.username}'
                    )
                )
            else:
                self.stdout.write(f'All profiles exist for user: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Done!'))
