from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Configuration for the integrations app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    verbose_name = 'Platform Integrations'
    
    def ready(self):
        """Import signals when app is ready."""
        import integrations.signals  # noqa

# Made with Bob
