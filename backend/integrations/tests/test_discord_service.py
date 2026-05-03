"""
Tests for Discord integration service.
"""
import logging
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import PlatformConnection, Channel
from ..services.discord_service import DiscordService

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class DiscordServiceTest(TestCase):
    """Test cases for DiscordService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456789',
            platform_username='testuser#1234',
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_expires_at=timezone.now() + timedelta(days=7)
        )
        
        self.service = DiscordService(self.connection)
    
    def test_get_platform_name(self):
        """Test platform name is 'discord'."""
        self.assertEqual(self.service.get_platform_name(), 'discord')
    
    def test_generate_authorization_url(self):
        """Test generating Discord OAuth URL."""
        result = self.service.generate_authorization_url()
        
        self.assertIn('url', result)
        self.assertIn('state', result)
        self.assertIn('discord.com/api/oauth2/authorize', result['url'])
        self.assertIn('client_id', result['url'])
        self.assertIn('state=' + result['state'], result['url'])
    
    def test_generate_authorization_url_with_state(self):
        """Test generating OAuth URL with provided state."""
        custom_state = 'custom_state_token'
        result = self.service.generate_authorization_url(custom_state)
        
        self.assertEqual(result['state'], custom_state)
        self.assertIn('state=' + custom_state, result['url'])
    
    @patch('integrations.services.discord_service.requests.post')
    def test_exchange_code_for_token_success(self, mock_post):
        """Test successful code exchange for token."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 604800,
            'token_type': 'Bearer'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.service.exchange_code_for_token('auth_code')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['access_token'], 'new_access_token')
        self.assertEqual(result['refresh_token'], 'new_refresh_token')
        self.assertEqual(result['expires_in'], 604800)
    
    @patch('integrations.services.discord_service.requests.post')
    def test_exchange_code_for_token_failure(self, mock_post):
        """Test failed code exchange."""
        mock_post.side_effect = Exception('API Error')
        
        result = self.service.exchange_code_for_token('invalid_code')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('integrations.services.discord_service.requests.get')
    def test_get_current_user_success(self, mock_get):
        """Test successful user info retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': '123456789',
            'username': 'testuser',
            'discriminator': '1234',
            'email': 'test@example.com',
            'avatar': 'avatar_hash'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.service.get_current_user('access_token')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user_id'], '123456789')
        self.assertEqual(result['username'], 'testuser#1234')
        self.assertEqual(result['email'], 'test@example.com')
    
    @patch('integrations.services.discord_service.requests.get')
    def test_validate_credentials_success(self, mock_get):
        """Test successful credential validation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': '123456789',
            'username': 'testuser',
            'discriminator': '1234'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.service.validate_credentials({'access_token': 'valid_token'})
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['user_id'], '123456789')
        self.assertEqual(result['username'], 'testuser#1234')
    
    def test_validate_credentials_missing_token(self):
        """Test validation fails without access token."""
        result = self.service.validate_credentials({})
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
    
    @patch('integrations.services.discord_service.requests.get')
    def test_fetch_user_guilds(self, mock_get):
        """Test fetching user's guilds."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'id': 'guild1',
                'name': 'Test Server 1',
                'icon': 'icon_hash',
                'approximate_member_count': 100
            },
            {
                'id': 'guild2',
                'name': 'Test Server 2',
                'icon': None,
                'approximate_member_count': 50
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        guilds = self.service.fetch_user_guilds('access_token')
        
        self.assertEqual(len(guilds), 2)
        self.assertEqual(guilds[0]['name'], 'Test Server 1')
        self.assertEqual(guilds[1]['name'], 'Test Server 2')
    
    @patch('integrations.services.discord_service.requests.get')
    def test_fetch_guild_channels(self, mock_get):
        """Test fetching channels for a guild."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'id': 'channel1',
                'name': 'general',
                'type': 0,  # Text channel
                'topic': 'General discussion'
            },
            {
                'id': 'channel2',
                'name': 'announcements',
                'type': 5,  # Announcement channel
                'topic': 'Important updates'
            },
            {
                'id': 'voice1',
                'name': 'Voice Channel',
                'type': 2  # Voice channel (should be filtered)
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        channels = self.service.fetch_guild_channels('guild1', 'access_token')
        
        self.assertEqual(len(channels), 3)
    
    @patch('integrations.services.discord_service.requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'refreshed_access_token',
            'refresh_token': 'refreshed_refresh_token',
            'expires_in': 604800
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.service.refresh_token()
        
        self.assertTrue(result)
        self.connection.refresh_from_db()
        self.assertEqual(self.connection.access_token, 'refreshed_access_token')
        self.assertEqual(self.connection.refresh_token, 'refreshed_refresh_token')
    
    @patch('integrations.services.discord_service.requests.post')
    def test_refresh_token_failure(self, mock_post):
        """Test failed token refresh."""
        mock_post.side_effect = Exception('Refresh failed')
        
        result = self.service.refresh_token()
        
        self.assertFalse(result)
        self.connection.refresh_from_db()
        self.assertEqual(self.connection.status, 'expired')
    
    def test_refresh_token_no_connection(self):
        """Test refresh fails without connection."""
        service = DiscordService()
        result = service.refresh_token()
        
        self.assertFalse(result)
    
    @patch.object(DiscordService, 'fetch_user_guilds')
    @patch.object(DiscordService, 'fetch_guild_channels')
    def test_fetch_channels(self, mock_fetch_guild_channels, mock_fetch_guilds):
        """Test fetching all channels."""
        mock_fetch_guilds.return_value = [
            {
                'id': 'guild1',
                'name': 'Test Server',
                'icon': 'icon_hash',
                'approximate_member_count': 100
            }
        ]
        
        mock_fetch_guild_channels.return_value = [
            {
                'id': 'channel1',
                'name': 'general',
                'type': 0,
                'topic': 'General chat'
            }
        ]
        
        channels = self.service.fetch_channels()
        
        # Should have 1 server + 1 channel
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]['channel_type'], 'discord_server')
        self.assertEqual(channels[1]['channel_type'], 'discord_channel')


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob