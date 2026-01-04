from django.core.management.base import BaseCommand
from notifications.models import Device
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Register a device token for a user'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, required=True, help='Username of the user')
        parser.add_argument('--token', type=str, required=True, help='Device token to register')

    def handle(self, *args, **kwargs):
        username = kwargs['user']
        token = kwargs['token']

        try:
            user = User.objects.get(username=username)
            Device.objects.filter(token=token).delete()  # Remove any existing devices with the same token
            Device.objects.create(user=user, token=token)
            self.stdout.write(self.style.SUCCESS(f'Device token registered for user {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))