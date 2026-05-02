"""
Management command to validate integrations setup.
Checks all required configurations, dependencies, and connections.
"""
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.core.exceptions import ImproperlyConfigured


class Command(BaseCommand):
    help = 'Validate integrations app setup and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues automatically',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Integrations Setup Validation'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        checks = [
            self.check_django_settings,
            self.check_database,
            self.check_redis,
            self.check_celery,
            self.check_discord_config,
            self.check_encryption_key,
            self.check_installed_apps,
            self.check_migrations,
        ]

        passed = 0
        failed = 0
        warnings = 0

        for check in checks:
            result = check()
            if result == 'pass':
                passed += 1
            elif result == 'fail':
                failed += 1
            elif result == 'warning':
                warnings += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Results: {passed} passed, {failed} failed, {warnings} warnings')
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if failed > 0:
            sys.exit(1)

    def check_django_settings(self):
        """Check Django settings configuration."""
        self.stdout.write('\n[1/8] Checking Django Settings...')
        
        try:
            # Check SECRET_KEY
            if not settings.SECRET_KEY or settings.SECRET_KEY.startswith('django-insecure'):
                self.stdout.write(
                    self.style.WARNING('  ⚠ SECRET_KEY is using default insecure value')
                )
                self.stdout.write('    Generate a new key: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"')
                return 'warning'
            
            # Check DEBUG
            if settings.DEBUG:
                self.stdout.write(
                    self.style.WARNING('  ⚠ DEBUG is True (should be False in production)')
                )
            
            # Check ALLOWED_HOSTS
            if not settings.ALLOWED_HOSTS and not settings.DEBUG:
                self.stdout.write(
                    self.style.ERROR('  ✗ ALLOWED_HOSTS is empty (required in production)')
                )
                return 'fail'
            
            self.stdout.write(self.style.SUCCESS('  ✓ Django settings OK'))
            return 'pass'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return 'fail'

    def check_database(self):
        """Check database connection and tables."""
        self.stdout.write('\n[2/8] Checking Database...')
        
        try:
            # Test connection
            connection.ensure_connection()
            
            # Check if tables exist
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='platform_connections'"
                )
                if not cursor.fetchone():
                    self.stdout.write(
                        self.style.ERROR('  ✗ platform_connections table not found')
                    )
                    self.stdout.write('    Run: python manage.py migrate')
                    return 'fail'
            
            self.stdout.write(self.style.SUCCESS('  ✓ Database connection OK'))
            self.stdout.write(self.style.SUCCESS('  ✓ Required tables exist'))
            return 'pass'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Database error: {str(e)}'))
            return 'fail'

    def check_redis(self):
        """Check Redis connection."""
        self.stdout.write('\n[3/8] Checking Redis...')
        
        try:
            import redis
            
            # Parse Redis URL
            broker_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
            
            # Extract host and port
            if broker_url.startswith('redis://'):
                parts = broker_url.replace('redis://', '').split(':')
                host = parts[0]
                port = int(parts[1].split('/')[0]) if len(parts) > 1 else 6379
            else:
                host = 'localhost'
                port = 6379
            
            # Test connection
            r = redis.Redis(host=host, port=port, socket_connect_timeout=2)
            r.ping()
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Redis connection OK ({host}:{port})'))
            return 'pass'
            
        except ImportError:
            self.stdout.write(self.style.ERROR('  ✗ Redis package not installed'))
            self.stdout.write('    Run: pip install redis')
            return 'fail'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Redis connection failed: {str(e)}'))
            self.stdout.write('    Ensure Redis is running: redis-server')
            return 'fail'

    def check_celery(self):
        """Check Celery configuration."""
        self.stdout.write('\n[4/8] Checking Celery...')
        
        try:
            import celery
            
            # Check broker URL
            broker_url = getattr(settings, 'CELERY_BROKER_URL', None)
            if not broker_url:
                self.stdout.write(
                    self.style.ERROR('  ✗ CELERY_BROKER_URL not configured')
                )
                return 'fail'
            
            # Check result backend
            result_backend = getattr(settings, 'CELERY_RESULT_BACKEND', None)
            if not result_backend:
                self.stdout.write(
                    self.style.WARNING('  ⚠ CELERY_RESULT_BACKEND not configured')
                )
            
            self.stdout.write(self.style.SUCCESS('  ✓ Celery configuration OK'))
            self.stdout.write('    To start worker: celery -A Infobyte worker --loglevel=info')
            self.stdout.write('    To start beat: celery -A Infobyte beat --loglevel=info')
            return 'pass'
            
        except ImportError:
            self.stdout.write(self.style.ERROR('  ✗ Celery package not installed'))
            self.stdout.write('    Run: pip install celery')
            return 'fail'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Celery error: {str(e)}'))
            return 'fail'

    def check_discord_config(self):
        """Check Discord OAuth configuration."""
        self.stdout.write('\n[5/8] Checking Discord Configuration...')
        
        try:
            client_id = getattr(settings, 'DISCORD_CLIENT_ID', '')
            client_secret = getattr(settings, 'DISCORD_CLIENT_SECRET', '')
            redirect_uri = getattr(settings, 'DISCORD_REDIRECT_URI', '')
            
            if not client_id:
                self.stdout.write(
                    self.style.WARNING('  ⚠ DISCORD_CLIENT_ID not configured')
                )
                self.stdout.write('    Discord OAuth will not work without this')
                return 'warning'
            
            if not client_secret:
                self.stdout.write(
                    self.style.WARNING('  ⚠ DISCORD_CLIENT_SECRET not configured')
                )
                return 'warning'
            
            if not redirect_uri:
                self.stdout.write(
                    self.style.WARNING('  ⚠ DISCORD_REDIRECT_URI not configured')
                )
                return 'warning'
            
            self.stdout.write(self.style.SUCCESS('  ✓ Discord OAuth configured'))
            self.stdout.write(f'    Client ID: {client_id[:10]}...')
            self.stdout.write(f'    Redirect URI: {redirect_uri}')
            return 'pass'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return 'fail'

    def check_encryption_key(self):
        """Check field encryption key."""
        self.stdout.write('\n[6/8] Checking Encryption Key...')
        
        try:
            from cryptography.fernet import Fernet
            
            key = getattr(settings, 'FIELD_ENCRYPTION_KEY', '')
            
            if not key:
                self.stdout.write(
                    self.style.ERROR('  ✗ FIELD_ENCRYPTION_KEY not configured')
                )
                self.stdout.write('    Generate key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
                return 'fail'
            
            # Validate key format
            try:
                Fernet(key.encode() if isinstance(key, str) else key)
                self.stdout.write(self.style.SUCCESS('  ✓ Encryption key valid'))
                return 'pass'
            except Exception:
                self.stdout.write(
                    self.style.ERROR('  ✗ Invalid encryption key format')
                )
                self.stdout.write('    Key must be 32 url-safe base64-encoded bytes')
                return 'fail'
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('  ✗ cryptography package not installed')
            )
            self.stdout.write('    Run: pip install cryptography')
            return 'fail'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return 'fail'

    def check_installed_apps(self):
        """Check if integrations app is in INSTALLED_APPS."""
        self.stdout.write('\n[7/8] Checking Installed Apps...')
        
        try:
            if 'integrations' not in settings.INSTALLED_APPS:
                self.stdout.write(
                    self.style.ERROR('  ✗ integrations not in INSTALLED_APPS')
                )
                self.stdout.write('    Add "integrations" to INSTALLED_APPS in settings.py')
                return 'fail'
            
            # Check required third-party apps
            required_apps = [
                'rest_framework',
                'corsheaders',
            ]
            
            missing = [app for app in required_apps if app not in settings.INSTALLED_APPS]
            
            if missing:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Missing apps: {", ".join(missing)}')
                )
                return 'warning'
            
            self.stdout.write(self.style.SUCCESS('  ✓ All required apps installed'))
            return 'pass'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return 'fail'

    def check_migrations(self):
        """Check if migrations are up to date."""
        self.stdout.write('\n[8/8] Checking Migrations...')
        
        try:
            from django.db.migrations.executor import MigrationExecutor
            
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {len(plan)} unapplied migrations')
                )
                self.stdout.write('    Run: python manage.py migrate')
                return 'warning'
            
            self.stdout.write(self.style.SUCCESS('  ✓ All migrations applied'))
            return 'pass'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return 'fail'

# Made with Bob