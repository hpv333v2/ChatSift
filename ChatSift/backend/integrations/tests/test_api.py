"""
API endpoint tests for integrations app.
"""
import logging
from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import PlatformConnection, Channel

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class DiscordOAuthAPITest(TestCase):
    """Test cases for Discord OAuth endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_discord_authorize_success(self):
        """Test successful Discord authorization URL generation."""
        response = self.client.get('/api/v1/integrations/discord/authorize/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('authorization_url', response.data['data'])
        self.assertIn('discord.com', response.data['data']['authorization_url'])
    
    def test_discord_authorize_unverified_email(self):
        """Test authorization fails for unverified email."""
        self.user.email_verified = False
        self.user.save()
        
        response = self.client.get('/api/v1/integrations/discord/authorize/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('integrations.views.DiscordService')
    def test_discord_callback_success(self, mock_service_class):
        """Test successful Discord OAuth callback."""
        # Setup session
        session = self.client.session
        session['discord_oauth_state'] = 'test_state'
        session.save()
        
        # Mock Discord service
        mock_service = Mock()
        mock_service.exchange_code_for_token.return_value = {
            'success': True,
            'access_token': 'access_token',
            'refresh_token': 'refresh_token',
            'expires_in': 604800
        }
        mock_service.get_current_user.return_value = {
            'success': True,
            'user_id': '123456789',
            'username': 'testuser#1234'
        }
        mock_service.sync_channels.return_value = {
            'success': True,
            'channels_synced': 5
        }
        mock_service_class.return_value = mock_service
        
        response = self.client.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'auth_code', 'state': 'test_state'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
    
    def test_discord_callback_invalid_state(self):
        """Test callback fails with invalid state."""
        response = self.client.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'auth_code', 'state': 'invalid_state'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TelegramConnectAPITest(TestCase):
    """Test cases for Telegram connection endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    @patch('integrations.views.TelegramService')
    def test_telegram_connect_success(self, mock_service_class):
        """Test successful Telegram bot connection."""
        mock_service = Mock()
        mock_service.validate_bot_token.return_value = {
            'valid': True,
            'bot_id': '123456789',
            'username': 'test_bot'
        }
        mock_service.sync_channels.return_value = {
            'success': True,
            'channels_synced': 3
        }
        mock_service_class.return_value = mock_service
        
        response = self.client.post(
            '/api/v1/integrations/telegram/connect/',
            {'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
    
    @patch('integrations.views.TelegramService')
    def test_telegram_connect_invalid_token(self, mock_service_class):
        """Test connection fails with invalid token."""
        mock_service = Mock()
        mock_service.validate_bot_token.return_value = {
            'valid': False,
            'error': 'Unauthorized'
        }
        mock_service_class.return_value = mock_service
        
        response = self.client.post(
            '/api/v1/integrations/telegram/connect/',
            {'bot_token': 'invalid_token'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_telegram_connect_unverified_email(self):
        """Test connection fails for unverified email."""
        self.user.email_verified = False
        self.user.save()
        
        response = self.client.post(
            '/api/v1/integrations/telegram/connect/',
            {'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ConnectionListAPITest(TestCase):
    """Test cases for connection list endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        
        # Create test connections
        self.discord_connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='token'
        )
        
        self.telegram_connection = PlatformConnection.objects.create(
            user=self.user,
            platform='telegram',
            platform_user_id='789012',
            platform_username='test_bot',
            bot_token='bot_token'
        )
    
    def test_list_connections(self):
        """Test listing all connections."""
        response = self.client.get('/api/v1/integrations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']['connections']), 2)
    
    def test_list_connections_unauthenticated(self):
        """Test listing fails without authentication."""
        self.client.credentials()  # Remove credentials
        response = self.client.get('/api/v1/integrations/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConnectionDetailAPITest(TestCase):
    """Test cases for connection detail endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='token'
        )
        
        # Create channels
        for i in range(3):
            Channel.objects.create(
                connection=self.connection,
                channel_id=f'channel_{i}',
                channel_name=f'Channel {i}',
                channel_type='discord_channel'
            )
    
    def test_get_connection_detail(self):
        """Test getting connection details."""
        response = self.client.get(f'/api/v1/integrations/{self.connection.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('channels', response.data['data'])
        self.assertEqual(len(response.data['data']['channels']), 3)
    
    def test_get_connection_not_found(self):
        """Test getting non-existent connection."""
        import uuid
        response = self.client.get(f'/api/v1/integrations/{uuid.uuid4()}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_connection(self):
        """Test deleting connection."""
        response = self.client.delete(f'/api/v1/integrations/{self.connection.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            PlatformConnection.objects.filter(id=self.connection.id).exists()
        )


class ConnectionRefreshAPITest(TestCase):
    """Test cases for connection refresh endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='token'
        )
    
    @patch('integrations.views.DiscordService')
    def test_refresh_connection_success(self, mock_service_class):
        """Test successful connection refresh."""
        mock_service = Mock()
        mock_service.sync_channels.return_value = {
            'success': True,
            'channels_synced': 5,
            'channels_added': 2,
            'channels_removed': 1
        }
        mock_service_class.return_value = mock_service
        
        response = self.client.post(f'/api/v1/integrations/{self.connection.id}/refresh/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('channels_synced', response.data['data'])
    
    @patch('integrations.views.DiscordService')
    def test_refresh_connection_failure(self, mock_service_class):
        """Test failed connection refresh."""
        mock_service = Mock()
        mock_service.sync_channels.return_value = {
            'success': False,
            'error': 'API Error'
        }
        mock_service_class.return_value = mock_service
        
        response = self.client.post(f'/api/v1/integrations/{self.connection.id}/refresh/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob