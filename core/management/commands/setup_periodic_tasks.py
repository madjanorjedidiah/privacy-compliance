"""Idempotent seed for Celery Beat periodic tasks.

Run on every deploy (entrypoint). Creates / refreshes the nightly
compliance-hygiene sweeps so Celery Beat actually has something to do.
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


SCHEDULES = [
    {
        'name': 'Nightly DPA expiry sweep',
        'task': 'vendors.tasks.flag_expiring_dpas',
        'hour': '1',
        'minute': '15',
    },
    {
        'name': 'Nightly training expiry sweep',
        'task': 'training.tasks.flag_expiring_training',
        'hour': '1',
        'minute': '30',
    },
]


class Command(BaseCommand):
    help = 'Ensure the standard Celery Beat periodic tasks exist.'

    def handle(self, *args, **options):
        loaded = 0
        for s in SCHEDULES:
            sched, _ = CrontabSchedule.objects.get_or_create(
                minute=s['minute'],
                hour=s['hour'],
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )
            PeriodicTask.objects.update_or_create(
                name=s['name'],
                defaults={'crontab': sched, 'task': s['task'], 'enabled': True},
            )
            loaded += 1
        self.stdout.write(self.style.SUCCESS(f'{loaded} periodic tasks in place.'))
