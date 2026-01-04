from django.core.management.base import BaseCommand
from firebase_admin import messaging
from notifications.models import Device
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Send notifications to users or groups of users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username of the user to send notification to')
        parser.add_argument('--group', type=str, help='Group name to send notification to')
        parser.add_argument('--title', type=str, required=True, help='Title of the notification')
        parser.add_argument('--body', type=str, required=True, help='Body of the notification')

    def handle(self, *args, **kwargs):
        user = kwargs.get('user')
        group = kwargs.get('group')
        title = kwargs['title']
        body = kwargs['body']

        if user:
            try:
                user_obj = User.objects.get(username=user)
                self.send_notification_to_user(user_obj, title, body)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {user} does not exist'))
        elif group:
            self.stdout.write(self.style.ERROR('Group notifications are not implemented yet'))
        else:
            self.stdout.write(self.style.ERROR('Please specify either a user or a group'))

    def send_notification_to_user(self, user, title, body):
        devices = Device.objects.filter(user=user)
        registration_tokens = [device.token for device in devices]

        if not registration_tokens:
            self.stdout.write(self.style.WARNING(f'No devices found for user {user.username}'))
            return

        for token in registration_tokens:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,
            )

            try:
                response = messaging.send(message)
                self.stdout.write(self.style.SUCCESS(f'Message sent to {token}: {response}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending notification to {token}: {e}'))