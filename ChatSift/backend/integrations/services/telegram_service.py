"""
Telegram integration service.
Handles bot validation, API communication, and group/channel syncing for Telegram.
"""
import logging
from typing import Dict, List, Optional, Any
import requests
from django.conf import settings
from .base_service import BaseIntegrationService

logger = logging.getLogger(__name__)


class TelegramService(BaseIntegrationService):
    """
    Service for Telegram platform integration.
    Handles bot token validation and Telegram Bot API interactions.
    """
    
    def __init__(self, connection=None):
        """Initialize Telegram service."""
        super().__init__(connection)
        self.api_url = self._get_setting('API_URL', 'https://api.telegram.org')
        self.timeout = self._get_setting('TIMEOUT', 30)
    
    def _get_setting(self, key: str, default=None):
        """Get Telegram-specific setting from Django settings."""
        integrations_config = getattr(settings, 'INTEGRATIONS', {})
        telegram_config = integrations_config.get('TELEGRAM', {})
        return telegram_config.get(key, default)
    
    def get_platform_name(self) -> str:
        """Return platform name."""
        return 'telegram'
    
    def _make_api_request(self, bot_token: str, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to Telegram Bot API.
        
        Args:
            bot_token: Telegram bot token
            method: API method name (e.g., 'getMe', 'getUpdates')
            params: Optional parameters for the API call
        
        Returns:
            Dictionary with API response or error
        """
        try:
            url = f"{self.api_url}/bot{bot_token}/{method}"
            
            response = requests.post(
                url,
                json=params or {},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('ok'):
                return {
                    'success': False,
                    'error': data.get('description', 'Unknown error')
                }
            
            return {
                'success': True,
                'result': data.get('result')
            }
            
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, f'_make_api_request:{method}')
    
    def validate_bot_token(self, bot_token: str) -> Dict[str, Any]:
        """
        Validate Telegram bot token by calling getMe.
        
        Args:
            bot_token: Telegram bot token to validate
        
        Returns:
            Dictionary with validation result
        """
        result = self._make_api_request(bot_token, 'getMe')
        
        if result.get('success'):
            bot_info = result['result']
            return {
                'valid': True,
                'bot_id': str(bot_info['id']),
                'username': bot_info['username'],
                'first_name': bot_info['first_name'],
                'can_join_groups': bot_info.get('can_join_groups', False),
                'can_read_all_group_messages': bot_info.get('can_read_all_group_messages', False),
            }
        else:
            return {
                'valid': False,
                'error': result.get('error', 'Failed to validate bot token')
            }
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Telegram credentials (bot token).
        
        Args:
            credentials: Dictionary with 'bot_token'
        
        Returns:
            Dictionary with validation result
        """
        bot_token = credentials.get('bot_token')
        if not bot_token:
            return {
                'valid': False,
                'error': 'Bot token is required'
            }
        
        validation_result = self.validate_bot_token(bot_token)
        
        if validation_result.get('valid'):
            return {
                'valid': True,
                'user_id': validation_result['bot_id'],
                'username': validation_result['username'],
            }
        else:
            return validation_result
    
    def get_updates(self, bot_token: str, offset: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get updates from Telegram (messages, group additions, etc.).
        
        Args:
            bot_token: Telegram bot token
            offset: Offset for getting updates
            limit: Maximum number of updates to retrieve
        
        Returns:
            List of update dictionaries
        """
        params = {
            'limit': limit,
            'timeout': 0  # Short polling
        }
        
        if offset is not None:
            params['offset'] = offset
        
        result = self._make_api_request(bot_token, 'getUpdates', params)
        
        if result.get('success'):
            return result['result']
        else:
            logger.error(f"Failed to get Telegram updates: {result.get('error')}")
            return []
    
    def get_chat(self, bot_token: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific chat.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to get information for
        
        Returns:
            Dictionary with chat information or None
        """
        params = {'chat_id': chat_id}
        result = self._make_api_request(bot_token, 'getChat', params)
        
        if result.get('success'):
            return result['result']
        else:
            logger.error(f"Failed to get chat {chat_id}: {result.get('error')}")
            return None
    
    def get_chat_member_count(self, bot_token: str, chat_id: str) -> Optional[int]:
        """
        Get the number of members in a chat.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID
        
        Returns:
            Member count or None if failed
        """
        params = {'chat_id': chat_id}
        result = self._make_api_request(bot_token, 'getChatMemberCount', params)
        
        if result.get('success'):
            return result['result']
        else:
            return None
    
    def fetch_channels(self) -> List[Dict[str, Any]]:
        """
        Fetch all available groups/channels from Telegram.
        
        Note: Telegram bots can only see groups they've been added to.
        We discover groups through the updates API.
        
        Returns:
            List of channel dictionaries formatted for database storage
        """
        if not self.connection:
            raise ValueError("Connection is required to fetch channels")
        
        bot_token = self.connection.bot_token
        channels = []
        seen_chats = set()
        
        # Get recent updates to discover groups
        updates = self.get_updates(bot_token, limit=100)
        
        for update in updates:
            # Extract chat information from various update types
            chat = None
            
            if 'message' in update:
                chat = update['message'].get('chat')
            elif 'my_chat_member' in update:
                chat = update['my_chat_member'].get('chat')
            elif 'channel_post' in update:
                chat = update['channel_post'].get('chat')
            
            if not chat:
                continue
            
            chat_id = str(chat['id'])
            chat_type = chat.get('type')
            
            # Only process groups and channels
            if chat_type not in ['group', 'supergroup', 'channel']:
                continue
            
            # Skip if already processed
            if chat_id in seen_chats:
                continue
            
            seen_chats.add(chat_id)
            
            # Get detailed chat information
            chat_info = self.get_chat(bot_token, chat_id)
            if not chat_info:
                continue
            
            # Determine channel type
            if chat_type == 'channel':
                channel_type = 'telegram_channel'
            else:
                channel_type = 'telegram_group'
            
            # Get member count
            member_count = self.get_chat_member_count(bot_token, chat_id)
            
            # Get chat photo URL if available
            photo_url = None
            if 'photo' in chat_info and 'big_file_id' in chat_info['photo']:
                # Note: Getting actual photo URL requires additional API call
                # For now, we'll just note that a photo exists
                photo_url = f"telegram://chat_photo/{chat_id}"
            
            channels.append({
                'channel_id': chat_id,
                'channel_name': chat_info.get('title', chat_info.get('username', 'Unknown')),
                'channel_type': channel_type,
                'member_count': member_count,
                'icon_url': photo_url,
                'description': chat_info.get('description'),
                'can_read_messages': True,
                'can_read_history': chat_info.get('type') != 'channel',  # Channels may have restrictions
            })
        
        return channels
    
    def refresh_token(self) -> bool:
        """
        Refresh token (not applicable for Telegram bots).
        Telegram bot tokens don't expire, so we just validate the token.
        
        Returns:
            True if token is still valid
        """
        if not self.connection or not self.connection.bot_token:
            logger.warning("Cannot refresh token: no connection or bot token")
            return False
        
        validation_result = self.validate_bot_token(self.connection.bot_token)
        
        if validation_result.get('valid'):
            self.update_connection_status('active')
            logger.info(f"Telegram bot token for connection {self.connection.id} is still valid")
            return True
        else:
            error_msg = validation_result.get('error', 'Token validation failed')
            self.update_connection_status('error', error_msg)
            logger.error(f"Telegram bot token validation failed: {error_msg}")
            return False
    
    def set_webhook(self, bot_token: str, webhook_url: str) -> bool:
        """
        Set webhook for receiving updates (optional feature).
        
        Args:
            bot_token: Telegram bot token
            webhook_url: URL where Telegram should send updates
        
        Returns:
            True if webhook was set successfully
        """
        params = {'url': webhook_url}
        result = self._make_api_request(bot_token, 'setWebhook', params)
        
        if result.get('success'):
            logger.info(f"Successfully set Telegram webhook to {webhook_url}")
            return True
        else:
            logger.error(f"Failed to set webhook: {result.get('error')}")
            return False
    
    def delete_webhook(self, bot_token: str) -> bool:
        """
        Delete webhook (switch back to polling mode).
        
        Args:
            bot_token: Telegram bot token
        
        Returns:
            True if webhook was deleted successfully
        """
        result = self._make_api_request(bot_token, 'deleteWebhook')
        
        if result.get('success'):
            logger.info("Successfully deleted Telegram webhook")
            return True
        else:
            logger.error(f"Failed to delete webhook: {result.get('error')}")
            return False


# Made with Bob