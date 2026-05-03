"""
Celery configuration for Infobyte project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Infobyte.settings')

app = Celery('Infobyte')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'sync-all-connections-hourly': {
        'task': 'integrations.tasks.sync_all_connections',
        'schedule': crontab(minute=0),  # Every hour
    },
    'refresh-discord-tokens-daily': {
        'task': 'integrations.tasks.refresh_expired_discord_tokens',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'check-connection-health-every-6-hours': {
        'task': 'integrations.tasks.check_connection_health',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'cleanup-failed-connections-weekly': {
        'task': 'integrations.tasks.cleanup_failed_connections',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday at 3 AM
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')

# Made with Bob