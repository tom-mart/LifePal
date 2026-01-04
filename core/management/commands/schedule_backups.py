from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = 'Schedule daily database backups using Django Q'

    def handle(self, *args, **kwargs):
        # Create or update the backup schedule
        schedule, created = Schedule.objects.update_or_create(
            name='Daily Database Backup',
            defaults={
                'func': 'core.tasks.backup_database',  # or 'core.tasks.backup_database_docker'
                'schedule_type': Schedule.DAILY,
                'repeats': -1,  # Run indefinitely
                'next_run': None,  # Start immediately
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created daily backup schedule'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Updated daily backup schedule'))
        
        self.stdout.write(f'Schedule ID: {schedule.id}')
        self.stdout.write(f'Next run: {schedule.next_run}')
