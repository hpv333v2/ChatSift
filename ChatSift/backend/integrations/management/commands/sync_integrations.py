"""
Management command to manually trigger integration syncing.
Useful for testing and manual operations.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from integrations.models import PlatformConnection
from integrations.tasks import (
    sync_connection_channels,
    sync_all_connections,
    sync_user_connections,
    check_connection_health,
    refresh_expired_discord_tokens,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Manually trigger integration syncing tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--connection',
            type=str,
            help='Sync specific connection by ID',
        )
        parser.add_argument(
            '--user',
            type=int,
            help='Sync all connections for specific user by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all active connections',
        )
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Run health check on all connections',
        )
        parser.add_argument(
            '--refresh-tokens',
            action='store_true',
            help='Refresh expiring Discord tokens',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            dest='use_async',
            help='Run tasks asynchronously via Celery (requires Celery worker)',
        )

    def handle(self, *args, **options):
        use_async = options.get('use_async', False)

        if options['connection']:
            self.sync_connection(options['connection'], use_async)
        elif options['user']:
            self.sync_user(options['user'], use_async)
        elif options['all']:
            self.sync_all(use_async)
        elif options['health_check']:
            self.health_check(use_async)
        elif options['refresh_tokens']:
            self.refresh_tokens(use_async)
        else:
            self.stdout.write(
                self.style.ERROR('Please specify an action: --connection, --user, --all, --health-check, or --refresh-tokens')
            )

    def sync_connection(self, connection_id, use_async):
        """Sync a specific connection."""
        try:
            connection = PlatformConnection.objects.get(id=connection_id)
            self.stdout.write(f'Syncing connection {connection_id} ({connection.platform})...')
            
            if use_async:
                result = sync_connection_channels.delay(connection_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Task queued with ID: {result.id}')
                )
            else:
                result = sync_connection_channels(connection_id)
                if result.get('success'):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully synced {result.get("channels_synced", 0)} channels'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Sync failed: {result.get("error")}')
                    )
        except PlatformConnection.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Connection {connection_id} not found')
            )

    def sync_user(self, user_id, use_async):
        """Sync all connections for a user."""
        try:
            user = User.objects.get(id=user_id)
            connections_count = PlatformConnection.objects.filter(
                user=user, status='active'
            ).count()
            
            self.stdout.write(
                f'Syncing {connections_count} connections for user {user_id}...'
            )
            
            if use_async:
                result = sync_user_connections.delay(user_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Task queued with ID: {result.id}')
                )
            else:
                result = sync_user_connections(user_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Queued {result.get("queued_successfully", 0)} sync tasks'
                    )
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {user_id} not found')
            )

    def sync_all(self, use_async):
        """Sync all active connections."""
        total = PlatformConnection.objects.filter(status='active').count()
        self.stdout.write(f'Syncing {total} active connections...')
        
        if use_async:
            result = sync_all_connections.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Task queued with ID: {result.id}')
            )
        else:
            result = sync_all_connections()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Queued {result.get("queued_successfully", 0)} sync tasks'
                )
            )

    def health_check(self, use_async):
        """Run health check on all connections."""
        total = PlatformConnection.objects.filter(status='active').count()
        self.stdout.write(f'Running health check on {total} connections...')
        
        if use_async:
            result = check_connection_health.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Task queued with ID: {result.id}')
            )
        else:
            result = check_connection_health()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Health check complete: {result.get("healthy", 0)} healthy, '
                    f'{result.get("unhealthy", 0)} unhealthy'
                )
            )

    def refresh_tokens(self, use_async):
        """Refresh expiring Discord tokens."""
        self.stdout.write('Refreshing expiring Discord tokens...')
        
        if use_async:
            result = refresh_expired_discord_tokens.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Task queued with ID: {result.id}')
            )
        else:
            result = refresh_expired_discord_tokens()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Queued {result.get("queued_successfully", 0)} refresh tasks'
                )
            )

# Made with Bob