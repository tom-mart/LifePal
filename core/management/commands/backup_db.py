from django.core.management.base import BaseCommand
from core.tasks import backup_database


class Command(BaseCommand):
    help = 'Create an immediate database backup'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating database backup...')
        result = backup_database()
        self.stdout.write(self.style.SUCCESS(result))
