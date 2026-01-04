from notifications.models import Device
from django.contrib.auth import get_user_model
from firebase_admin import messaging

User = get_user_model()

def send_notification_task(args):
    username, title, body = args
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return f"User {username} does not exist"

    devices = Device.objects.filter(user=user)
    registration_tokens = [device.token for device in devices]
    if not registration_tokens:
        return f"No devices found for user {username}"

    for token in registration_tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        try:
            messaging.send(message)
        except Exception as e:
            return f"Error sending notification to {token}: {e}"
    return f"Notification sent to {username}"
