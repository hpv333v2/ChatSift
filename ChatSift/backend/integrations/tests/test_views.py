"""
View-level tests for integrations app.
Tests view logic, permissions, and response formatting.
"""
import logging
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from rest_framework import status
from ..models import PlatformConnection, Channel
from ..views import (
    DiscordAuthorizeView,
    DiscordCallbackView,
    TelegramConnectView,
    ConnectionListView,
    ConnectionDetailView,
    ConnectionRefreshView
)

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class DiscordAuthorizeViewTest(TestCase):
    """Test cases for DiscordAuthorizeView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = DiscordAuthorizeView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
    
    def test_generate_authorization_url(self):
        """Test authorization URL generation."""
        request = self.factory.get('/api/v1/integrations/discord/authorize/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authorization_url', response.data['data'])
        self.assertIn('state', response.data['data'])
    
    def test_state_stored_in_session(self):
        """Test that OAuth state is stored in session."""
        request = self.factory.get('/api/v1/integrations/discord/authorize/')
        request.session = {}
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertIn('discord_oauth_state', request.session)
        self.assertEqual(
            request.session['discord_oauth_state'],
            response.data['data']['state']
        )
    
    def test_unverified_email_rejected(self):
        """Test that unverified email is rejected."""
        self.user.email_verified = False
        self.user.save()
        
        request = self.factory.get('/api/v1/integrations/discord/authorize/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DiscordCallbackViewTest(TestCase):
    """Test cases for DiscordCallbackView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = DiscordCallbackView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
    
    @patch('integrations.views.DiscordService')
    def test_successful_callback(self, mock_service_class):
        """Test successful OAuth callback processing."""
        # Setup mock
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
        
        # Setup request
        request = self.factory.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'auth_code', 'state': 'test_state'}
        )
        request.session = {'discord_oauth_state': 'test_state'}
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
    
    def test_missing_state_rejected(self):
        """Test that missing state parameter is rejected."""
        request = self.factory.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'auth_code'}
        )
        request.session = {}
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_state_mismatch_rejected(self):
        """Test that state mismatch is rejected."""
        request = self.factory.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'auth_code', 'state': 'wrong_state'}
        )
        request.session = {'discord_oauth_state': 'correct_state'}
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('integrations.views.DiscordService')
    def test_token_exchange_failure(self, mock_service_class):
        """Test handling of token exchange failure."""
        mock_service = Mock()
        mock_service.exchange_code_for_token.return_value = {
            'success': False,
            'error': 'Invalid code'
        }
        mock_service_class.return_value = mock_service
        
        request = self.factory.get(
            '/api/v1/integrations/discord/callback/',
            {'code': 'invalid_code', 'state': 'test_state'}
        )
        request.session = {'discord_oauth_state': 'test_state'}
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TelegramConnectViewTest(TestCase):
    """Test cases for TelegramConnectView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = TelegramConnectView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
    
    @patch('integrations.views.TelegramService')
    def test_successful_connection(self, mock_service_class):
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
        
        request = self.factory.post(
            '/api/v1/integrations/telegram/connect/',
            {'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'},
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
    
    @patch('integrations.views.TelegramService')
    def test_invalid_token_rejected(self, mock_service_class):
        """Test that invalid token is rejected."""
        mock_service = Mock()
        mock_service.validate_bot_token.return_value = {
            'valid': False,
            'error': 'Unauthorized'
        }
        mock_service_class.return_value = mock_service
        
        request = self.factory.post(
            '/api/v1/integrations/telegram/connect/',
            {'bot_token': 'invalid_token'},
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ConnectionListViewTest(TestCase):
    """Test cases for ConnectionListView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ConnectionListView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        
        # Create test connections
        PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='token'
        )
        
        PlatformConnection.objects.create(
            user=self.user,
            platform='telegram',
            platform_user_id='789012',
            platform_username='test_bot',
            bot_token='bot_token'
        )
    
    def test_list_user_connections(self):
        """Test listing user's connections."""
        request = self.factory.get('/api/v1/integrations/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['connections']), 2)
    
    def test_only_user_connections_returned(self):
        """Test that only user's own connections are returned."""
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='TestPass123!'
        )
        PlatformConnection.objects.create(
            user=other_user,
            platform='discord',
            platform_user_id='999999',
            platform_username='otheruser#5678',
            access_token='other_token'
        )
        
        request = self.factory.get('/api/v1/integrations/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(len(response.data['data']['connections']), 2)


class ConnectionDetailViewTest(TestCase):
    """Test cases for ConnectionDetailView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ConnectionDetailView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        
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
        request = self.factory.get(f'/api/v1/integrations/{self.connection.id}/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=self.connection.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('channels', response.data['data'])
        self.assertEqual(len(response.data['data']['channels']), 3)
    
    def test_delete_connection(self):
        """Test deleting connection."""
        request = self.factory.delete(f'/api/v1/integrations/{self.connection.id}/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=self.connection.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            PlatformConnection.objects.filter(id=self.connection.id).exists()
        )
    
    def test_cannot_access_other_user_connection(self):
        """Test that user cannot access another user's connection."""
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='TestPass123!'
        )
        
        request = self.factory.get(f'/api/v1/integrations/{self.connection.id}/')
        force_authenticate(request, user=other_user)
        
        response = self.view(request, pk=self.connection.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ConnectionRefreshViewTest(TestCase):
    """Test cases for ConnectionRefreshView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ConnectionRefreshView.as_view()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            email_verified=True
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='token'
        )
    
    @patch('integrations.views.DiscordService')
    def test_successful_refresh(self, mock_service_class):
        """Test successful connection refresh."""
        mock_service = Mock()
        mock_service.sync_channels.return_value = {
            'success': True,
            'channels_synced': 5,
            'channels_added': 2,
            'channels_removed': 1
        }
        mock_service_class.return_value = mock_service
        
        request = self.factory.post(f'/api/v1/integrations/{self.connection.id}/refresh/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=self.connection.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('channels_synced', response.data['data'])
    
    @patch('integrations.views.DiscordService')
    def test_refresh_failure_handled(self, mock_service_class):
        """Test handling of refresh failure."""
        mock_service = Mock()
        mock_service.sync_channels.return_value = {
            'success': False,
            'error': 'API Error'
        }
        mock_service_class.return_value = mock_service
        
        request = self.factory.post(f'/api/v1/integrations/{self.connection.id}/refresh/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=self.connection.id)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob