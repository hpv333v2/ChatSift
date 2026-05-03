"""
Base integration service class for platform integrations.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseIntegrationService(ABC):
    """
    Abstract base class for platform integration services.
    Provides common functionality for Discord, Telegram, and future platforms.
    """
    
    def __init__(self, connection=None):
        """
        Initialize the integration service.
        
        Args:
            connection: PlatformConnection instance (optional)
        """
        self.connection = connection
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (e.g., 'discord', 'telegram')."""
        pass
    
    @abstractmethod
    def validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate platform credentials.
        
        Args:
            credentials: Dictionary containing platform-specific credentials
        
        Returns:
            Dictionary with validation result:
            {
                'valid': bool,
                'user_id': str (if valid),
                'username': str (if valid),
                'error': str (if invalid)
            }
        """
        pass
    
    @abstractmethod
    def fetch_channels(self) -> List[Dict[str, Any]]:
        """
        Fetch available channels/servers from the platform.
        
        Returns:
            List of channel dictionaries with platform-specific data
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """
        Refresh the access token if supported by the platform.
        
        Returns:
            True if token was refreshed successfully, False otherwise
        """
        pass
    
    def handle_api_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle API errors consistently across platforms.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        
        Returns:
            Dictionary with error information
        """
        error_message = str(error)
        logger.error(
            f"{self.platform_name} API error in {context}: {error_message}",
            exc_info=True
        )
        
        return {
            'success': False,
            'error': error_message,
            'context': context
        }
    
    def update_connection_status(self, status: str, error_message: Optional[str] = None):
        """
        Update the connection status in the database.
        
        Args:
            status: New status ('active', 'expired', 'revoked', 'error')
            error_message: Error message if status is 'error'
        """
        if not self.connection:
            return
        
        self.connection.status = status
        if error_message:
            self.connection.error_message = error_message
        else:
            self.connection.error_message = None
        
        self.connection.save(update_fields=['status', 'error_message', 'updated_at'])
        
        logger.info(
            f"Updated {self.platform_name} connection {self.connection.id} "
            f"status to {status}"
        )
    
    def update_last_sync(self):
        """Update the last sync timestamp for the connection."""
        if not self.connection:
            return
        
        self.connection.last_sync = timezone.now()
        self.connection.save(update_fields=['last_sync', 'updated_at'])
    
    def is_token_valid(self) -> bool:
        """
        Check if the current token is valid (not expired).
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.connection:
            return False
        
        return not self.connection.is_token_expired()
    
    def sync_channels(self) -> Dict[str, Any]:
        """
        Sync channels from the platform to the database.
        
        Returns:
            Dictionary with sync results:
            {
                'success': bool,
                'channels_synced': int,
                'channels_added': int,
                'channels_removed': int,
                'error': str (if failed)
            }
        """
        if not self.connection:
            return {
                'success': False,
                'error': 'No connection provided'
            }
        
        try:
            # Fetch channels from platform
            platform_channels = self.fetch_channels()
            
            # Get existing channels
            from ..models import Channel
            existing_channels = {
                ch.channel_id: ch 
                for ch in self.connection.channels.all()
            }
            
            platform_channel_ids = set()
            channels_added = 0
            channels_updated = 0
            
            # Update or create channels
            for channel_data in platform_channels:
                channel_id = channel_data['channel_id']
                platform_channel_ids.add(channel_id)
                
                if channel_id in existing_channels:
                    # Update existing channel
                    channel = existing_channels[channel_id]
                    for key, value in channel_data.items():
                        if key != 'channel_id':
                            setattr(channel, key, value)
                    channel.is_active = True
                    channel.save()
                    channels_updated += 1
                else:
                    # Create new channel
                    Channel.objects.create(
                        connection=self.connection,
                        **channel_data
                    )
                    channels_added += 1
            
            # Mark removed channels as inactive
            channels_removed = 0
            for channel_id, channel in existing_channels.items():
                if channel_id not in platform_channel_ids and channel.is_active:
                    channel.mark_inactive()
                    channels_removed += 1
            
            # Update sync timestamp
            self.update_last_sync()
            
            # Update connection status to active
            self.update_connection_status('active')
            
            logger.info(
                f"Synced {self.platform_name} channels for connection {self.connection.id}: "
                f"{channels_added} added, {channels_updated} updated, {channels_removed} removed"
            )
            
            return {
                'success': True,
                'channels_synced': len(platform_channels),
                'channels_added': channels_added,
                'channels_updated': channels_updated,
                'channels_removed': channels_removed
            }
            
        except Exception as e:
            error_result = self.handle_api_error(e, 'sync_channels')
            self.update_connection_status('error', error_result['error'])
            return error_result


# Made with Bob