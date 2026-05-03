"""
Celery tasks for integrations app.
Handles background processing for channel syncing, token refresh, and health checks.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from celery import shared_task
from .models import PlatformConnection
from .services.discord_service import DiscordService
from .services.telegram_service import TelegramService

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_connection_channels(self, connection_id):
    """
    Sync channels for a specific connection.
    
    Args:
        connection_id: UUID of the PlatformConnection
        
    Returns:
        dict: Sync results with channels_synced count
    """
    try:
        connection = PlatformConnection.objects.get(id=connection_id)
        
        # Get appropriate service
        if connection.platform == 'discord':
            service = DiscordService(connection)
        elif connection.platform == 'telegram':
            service = TelegramService(connection)
        else:
            logger.error(f"Unknown platform: {connection.platform}")
            return {'success': False, 'error': 'Unknown platform'}
        
        # Sync channels
        result = service.sync_channels()
        
        if result.get('success'):
            logger.info(
                f"Successfully synced {result.get('channels_synced', 0)} channels "
                f"for connection {connection_id}"
            )
        else:
            logger.warning(
                f"Failed to sync channels for connection {connection_id}: "
                f"{result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except PlatformConnection.DoesNotExist:
        logger.error(f"Connection {connection_id} not found")
        return {'success': False, 'error': 'Connection not found'}
    except Exception as exc:
        logger.exception(f"Error syncing connection {connection_id}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task
def sync_all_connections():
    """
    Sync channels for all active connections.
    Runs hourly via Celery Beat.
    
    Returns:
        dict: Summary of sync operations
    """
    active_connections = PlatformConnection.objects.filter(
        status='active'
    ).select_related('user')
    
    total = active_connections.count()
    success_count = 0
    failed_count = 0
    
    logger.info(f"Starting sync for {total} active connections")
    
    for connection in active_connections:
        try:
            # Queue individual sync task
            result = sync_connection_channels.delay(str(connection.id))
            success_count += 1
        except Exception as e:
            logger.error(
                f"Failed to queue sync for connection {connection.id}: {str(e)}"
            )
            failed_count += 1
    
    summary = {
        'total_connections': total,
        'queued_successfully': success_count,
        'failed_to_queue': failed_count,
        'timestamp': timezone.now().isoformat()
    }
    
    logger.info(f"Sync all connections completed: {summary}")
    return summary


@shared_task(bind=True, max_retries=3, default_retry_delay=600)
def refresh_discord_token(self, connection_id):
    """
    Refresh Discord OAuth token for a connection.
    
    Args:
        connection_id: UUID of the PlatformConnection
        
    Returns:
        dict: Refresh results
    """
    try:
        connection = PlatformConnection.objects.get(
            id=connection_id,
            platform='discord'
        )
        
        service = DiscordService(connection)
        result = service.refresh_access_token()
        
        if result.get('success'):
            logger.info(f"Successfully refreshed token for connection {connection_id}")
        else:
            logger.warning(
                f"Failed to refresh token for connection {connection_id}: "
                f"{result.get('error', 'Unknown error')}"
            )
            
            # Mark connection as error if refresh fails
            connection.status = 'error'
            connection.error_message = result.get('error', 'Token refresh failed')
            connection.save(update_fields=['status', 'error_message', 'updated_at'])
        
        return result
        
    except PlatformConnection.DoesNotExist:
        logger.error(f"Discord connection {connection_id} not found")
        return {'success': False, 'error': 'Connection not found'}
    except Exception as exc:
        logger.exception(f"Error refreshing token for connection {connection_id}")
        raise self.retry(exc=exc)


@shared_task
def refresh_expired_discord_tokens():
    """
    Refresh Discord tokens that are about to expire (within 24 hours).
    Runs daily via Celery Beat.
    
    Returns:
        dict: Summary of refresh operations
    """
    # Find Discord connections with tokens expiring in the next 24 hours
    expiry_threshold = timezone.now() + timedelta(hours=24)
    
    expiring_connections = PlatformConnection.objects.filter(
        platform='discord',
        status='active',
        token_expires_at__lte=expiry_threshold,
        token_expires_at__gt=timezone.now()
    )
    
    total = expiring_connections.count()
    success_count = 0
    failed_count = 0
    
    logger.info(f"Starting token refresh for {total} expiring Discord connections")
    
    for connection in expiring_connections:
        try:
            result = refresh_discord_token.delay(str(connection.id))
            success_count += 1
        except Exception as e:
            logger.error(
                f"Failed to queue token refresh for connection {connection.id}: {str(e)}"
            )
            failed_count += 1
    
    summary = {
        'total_expiring': total,
        'queued_successfully': success_count,
        'failed_to_queue': failed_count,
        'timestamp': timezone.now().isoformat()
    }
    
    logger.info(f"Token refresh completed: {summary}")
    return summary


@shared_task
def check_connection_health():
    """
    Check health of all active connections.
    Attempts to verify connection is still valid by making a test API call.
    Runs every 6 hours via Celery Beat.
    
    Returns:
        dict: Summary of health check operations
    """
    active_connections = PlatformConnection.objects.filter(
        status='active'
    ).select_related('user')
    
    total = active_connections.count()
    healthy_count = 0
    unhealthy_count = 0
    
    logger.info(f"Starting health check for {total} active connections")
    
    for connection in active_connections:
        try:
            # Get appropriate service
            if connection.platform == 'discord':
                service = DiscordService(connection)
                # Try to get current user info as health check
                result = service.get_current_user()
            elif connection.platform == 'telegram':
                service = TelegramService(connection)
                # Try to get bot info as health check
                result = service.validate_bot_token()
            else:
                logger.warning(f"Unknown platform for connection {connection.id}")
                continue
            
            if result.get('success') or result.get('valid'):
                healthy_count += 1
                # Update last_synced timestamp
                connection.last_synced = timezone.now()
                connection.save(update_fields=['last_synced', 'updated_at'])
            else:
                unhealthy_count += 1
                # Mark as error
                connection.status = 'error'
                connection.error_message = result.get('error', 'Health check failed')
                connection.save(update_fields=['status', 'error_message', 'updated_at'])
                
                logger.warning(
                    f"Connection {connection.id} failed health check: "
                    f"{connection.error_message}"
                )
                
        except Exception as e:
            logger.error(
                f"Error checking health for connection {connection.id}: {str(e)}"
            )
            unhealthy_count += 1
    
    summary = {
        'total_checked': total,
        'healthy': healthy_count,
        'unhealthy': unhealthy_count,
        'timestamp': timezone.now().isoformat()
    }
    
    logger.info(f"Health check completed: {summary}")
    return summary


@shared_task
def cleanup_failed_connections():
    """
    Clean up connections that have been in error state for more than 30 days.
    Runs weekly via Celery Beat.
    
    Returns:
        dict: Summary of cleanup operations
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_failed_connections = PlatformConnection.objects.filter(
        status='error',
        updated_at__lt=cutoff_date
    )
    
    total = old_failed_connections.count()
    
    logger.info(f"Cleaning up {total} old failed connections")
    
    # Delete old failed connections
    deleted_count, _ = old_failed_connections.delete()
    
    summary = {
        'total_found': total,
        'deleted': deleted_count,
        'cutoff_date': cutoff_date.isoformat(),
        'timestamp': timezone.now().isoformat()
    }
    
    logger.info(f"Cleanup completed: {summary}")
    return summary


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def sync_user_connections(self, user_id):
    """
    Sync all connections for a specific user.
    Useful for manual triggers or after user actions.
    
    Args:
        user_id: ID of the User
        
    Returns:
        dict: Summary of sync operations for user
    """
    try:
        user = User.objects.get(id=user_id)
        connections = PlatformConnection.objects.filter(
            user=user,
            status='active'
        )
        
        total = connections.count()
        success_count = 0
        failed_count = 0
        
        logger.info(f"Starting sync for {total} connections for user {user_id}")
        
        for connection in connections:
            try:
                result = sync_connection_channels.delay(str(connection.id))
                success_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to queue sync for connection {connection.id}: {str(e)}"
                )
                failed_count += 1
        
        summary = {
            'user_id': user_id,
            'total_connections': total,
            'queued_successfully': success_count,
            'failed_to_queue': failed_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"User sync completed: {summary}")
        return summary
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'success': False, 'error': 'User not found'}
    except Exception as exc:
        logger.exception(f"Error syncing connections for user {user_id}")
        raise self.retry(exc=exc)

# Made with Bob