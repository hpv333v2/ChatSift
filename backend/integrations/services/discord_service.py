"""
Discord integration service.
Handles OAuth flow, API communication, and channel syncing for Discord.
"""
import logging
import secrets
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from datetime import timedelta
import requests
from django.conf import settings
from django.utils import timezone
from .base_service import BaseIntegrationService

logger = logging.getLogger(__name__)


class DiscordService(BaseIntegrationService):
    """
    Service for Discord platform integration.
    Handles OAuth2 flow and Discord API interactions.
    """
    
    API_BASE_URL = "https://discord.com/api/v10"
    OAUTH_AUTHORIZE_URL = "https://discord.com/api/oauth2/authorize"
    OAUTH_TOKEN_URL = "https://discord.com/api/oauth2/token"
    
    def __init__(self, connection=None):
        """Initialize Discord service."""
        super().__init__(connection)
        self.client_id = self._get_setting('CLIENT_ID')
        self.client_secret = self._get_setting('CLIENT_SECRET')
        self.redirect_uri = self._get_setting('REDIRECT_URI')
        self.scopes = self._get_setting('SCOPES', ['identify', 'guilds'])
    
    def _get_setting(self, key: str, default=None):
        """Get Discord-specific setting from Django settings."""
        integrations_config = getattr(settings, 'INTEGRATIONS', {})
        discord_config = integrations_config.get('DISCORD', {})
        return discord_config.get(key, default)
    
    def get_platform_name(self) -> str:
        """Return platform name."""
        return 'discord'
    
    def generate_authorization_url(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate Discord OAuth2 authorization URL.
        
        Args:
            state: CSRF protection state token (generated if not provided)
        
        Returns:
            Dictionary with 'url' and 'state'
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'state': state,
        }
        
        url = f"{self.OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        
        return {
            'url': url,
            'state': state
        }
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Dictionary with token data or error
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
            }
            
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            return {
                'success': True,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in', 604800),  # Default 7 days
                'token_type': token_data.get('token_type', 'Bearer'),
            }
            
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, 'exchange_code_for_token')
    
    def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user information from Discord.
        
        Args:
            access_token: Discord access token
        
        Returns:
            Dictionary with user data or error
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(
                f"{self.API_BASE_URL}/users/@me",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                'success': True,
                'user_id': user_data['id'],
                'username': f"{user_data['username']}#{user_data['discriminator']}",
                'email': user_data.get('email'),
                'avatar': user_data.get('avatar'),
            }
            
        except requests.exceptions.RequestException as e:
            return self.handle_api_error(e, 'get_current_user')
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Discord credentials (access token).
        
        Args:
            credentials: Dictionary with 'access_token'
        
        Returns:
            Dictionary with validation result
        """
        access_token = credentials.get('access_token')
        if not access_token:
            return {
                'valid': False,
                'error': 'Access token is required'
            }
        
        user_result = self.get_current_user(access_token)
        
        if user_result.get('success'):
            return {
                'valid': True,
                'user_id': user_result['user_id'],
                'username': user_result['username'],
            }
        else:
            return {
                'valid': False,
                'error': user_result.get('error', 'Failed to validate credentials')
            }
    
    def fetch_user_guilds(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Fetch user's Discord guilds (servers).
        
        Args:
            access_token: Discord access token
        
        Returns:
            List of guild dictionaries
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(
                f"{self.API_BASE_URL}/users/@me/guilds",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Discord guilds: {e}")
            return []
    
    def fetch_guild_channels(self, guild_id: str, access_token: str) -> List[Dict[str, Any]]:
        """
        Fetch channels for a specific guild.
        
        Args:
            guild_id: Discord guild ID
            access_token: Discord access token
        
        Returns:
            List of channel dictionaries
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(
                f"{self.API_BASE_URL}/guilds/{guild_id}/channels",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch channels for guild {guild_id}: {e}")
            return []
    
    def fetch_channels(self) -> List[Dict[str, Any]]:
        """
        Fetch all available channels from Discord.
        
        Returns:
            List of channel dictionaries formatted for database storage
        """
        if not self.connection:
            raise ValueError("Connection is required to fetch channels")
        
        access_token = self.connection.access_token
        channels = []
        
        # Fetch user's guilds
        guilds = self.fetch_user_guilds(access_token)
        
        for guild in guilds:
            guild_id = guild['id']
            guild_name = guild['name']
            
            # Add guild as a channel (server)
            channels.append({
                'channel_id': guild_id,
                'channel_name': guild_name,
                'channel_type': 'discord_server',
                'member_count': guild.get('approximate_member_count'),
                'icon_url': self._get_guild_icon_url(guild),
                'description': guild.get('description'),
                'can_read_messages': True,
                'can_read_history': True,
            })
            
            # Fetch channels within the guild
            guild_channels = self.fetch_guild_channels(guild_id, access_token)
            
            for channel in guild_channels:
                # Only include text channels
                if channel.get('type') in [0, 5]:  # 0=text, 5=announcement
                    channels.append({
                        'channel_id': channel['id'],
                        'channel_name': f"{guild_name} / {channel['name']}",
                        'channel_type': 'discord_channel',
                        'description': channel.get('topic'),
                        'can_read_messages': True,
                        'can_read_history': True,
                    })
        
        return channels
    
    def _get_guild_icon_url(self, guild: Dict[str, Any]) -> Optional[str]:
        """Generate guild icon URL if icon exists."""
        if guild.get('icon'):
            guild_id = guild['id']
            icon_hash = guild['icon']
            return f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.png"
        return None
    
    def refresh_token(self) -> bool:
        """
        Refresh the Discord access token.
        
        Returns:
            True if token was refreshed successfully
        """
        if not self.connection or not self.connection.refresh_token:
            logger.warning("Cannot refresh token: no connection or refresh token")
            return False
        
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.connection.refresh_token,
            }
            
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update connection with new tokens
            self.connection.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.connection.refresh_token = token_data['refresh_token']
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 604800)
            self.connection.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            
            self.connection.save(update_fields=[
                'access_token',
                'refresh_token',
                'token_expires_at',
                'updated_at'
            ])
            
            logger.info(f"Successfully refreshed Discord token for connection {self.connection.id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh Discord token: {e}")
            self.update_connection_status('expired', str(e))
            return False


# Made with Bob