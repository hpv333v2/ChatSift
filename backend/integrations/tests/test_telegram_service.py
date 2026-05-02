"""
Tests for Telegram integration service.
"""
import logging
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import PlatformConnection
from ..services.telegram_service import TelegramService

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class TelegramServiceTest(TestCase):
    """Test cases for TelegramService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='telegram',
            platform_user_id='123456789',
            platform_username='test_bot',
            bot_token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
        )
        
        self.service = TelegramService(self.connection)
    
    def test_get_platform_name(self):
        """Test platform name is 'telegram'."""
        self.assertEqual(self.service.get_platform_name(), 'telegram')
    
    @patch('integrations.services.telegram_service.requests.post')
    def test_make_api_request_success(self, mock_post):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'ok': True,
            'result': {'id': 123, 'username': 'test_bot'}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.service._make_api_request('bot_token', 'getMe')
        
        self.assertTrue(result['success'])
        self.assertIn('result', result)
        self.assertEqual(result['result']['username'], 'test_bot')
    
    @patch('integrations.services.telegram_service.requests.post')
    def test_make_api_request_api_error(self, mock_post):
        """Test API request with Telegram API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'ok': False,
            'description': 'Unauthorized'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.service._make_api_request('invalid_token', 'getMe')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Unauthorized')
    
    @patch('integrations.services.telegram_service.requests.post')
    def test_make_api_request_network_error(self, mock_post):
        """Test API request with network error."""
        mock_post.side_effect = Exception('Network error')
        
        result = self.service._make_api_request('bot_token', 'getMe')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_validate_bot_token_success(self, mock_api_request):
        """Test successful bot token validation."""
        mock_api_request.return_value = {
            'success': True,
            'result': {
                'id': 123456789,
                'username': 'test_bot',
                'first_name': 'Test Bot',
                'can_join_groups': True,
                'can_read_all_group_messages': True
            }
        }
        
        result = self.service.validate_bot_token('valid_token')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['bot_id'], '123456789')
        self.assertEqual(result['username'], 'test_bot')
        self.assertTrue(result['can_join_groups'])
    
    @patch.object(TelegramService, '_make_api_request')
    def test_validate_bot_token_failure(self, mock_api_request):
        """Test failed bot token validation."""
        mock_api_request.return_value = {
            'success': False,
            'error': 'Unauthorized'
        }
        
        result = self.service.validate_bot_token('invalid_token')
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
    
    @patch.object(TelegramService, 'validate_bot_token')
    def test_validate_credentials_success(self, mock_validate):
        """Test successful credential validation."""
        mock_validate.return_value = {
            'valid': True,
            'bot_id': '123456789',
            'username': 'test_bot'
        }
        
        result = self.service.validate_credentials({'bot_token': 'valid_token'})
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['user_id'], '123456789')
        self.assertEqual(result['username'], 'test_bot')
    
    def test_validate_credentials_missing_token(self):
        """Test validation fails without bot token."""
        result = self.service.validate_credentials({})
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_get_updates(self, mock_api_request):
        """Test getting updates from Telegram."""
        mock_api_request.return_value = {
            'success': True,
            'result': [
                {
                    'update_id': 1,
                    'message': {
                        'message_id': 1,
                        'chat': {
                            'id': -1001234567890,
                            'type': 'supergroup',
                            'title': 'Test Group'
                        }
                    }
                }
            ]
        }
        
        updates = self.service.get_updates('bot_token')
        
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]['update_id'], 1)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_get_chat(self, mock_api_request):
        """Test getting chat information."""
        mock_api_request.return_value = {
            'success': True,
            'result': {
                'id': -1001234567890,
                'type': 'supergroup',
                'title': 'Test Group',
                'description': 'A test group'
            }
        }
        
        chat = self.service.get_chat('bot_token', '-1001234567890')
        
        self.assertIsNotNone(chat)
        self.assertEqual(chat['title'], 'Test Group')
        self.assertEqual(chat['type'], 'supergroup')
    
    @patch.object(TelegramService, '_make_api_request')
    def test_get_chat_member_count(self, mock_api_request):
        """Test getting chat member count."""
        mock_api_request.return_value = {
            'success': True,
            'result': 42
        }
        
        count = self.service.get_chat_member_count('bot_token', '-1001234567890')
        
        self.assertEqual(count, 42)
    
    @patch.object(TelegramService, 'get_updates')
    @patch.object(TelegramService, 'get_chat')
    @patch.object(TelegramService, 'get_chat_member_count')
    def test_fetch_channels(self, mock_member_count, mock_get_chat, mock_get_updates):
        """Test fetching all channels."""
        mock_get_updates.return_value = [
            {
                'update_id': 1,
                'message': {
                    'chat': {
                        'id': -1001234567890,
                        'type': 'supergroup',
                        'title': 'Test Group'
                    }
                }
            },
            {
                'update_id': 2,
                'channel_post': {
                    'chat': {
                        'id': -1009876543210,
                        'type': 'channel',
                        'title': 'Test Channel'
                    }
                }
            }
        ]
        
        mock_get_chat.side_effect = [
            {
                'id': -1001234567890,
                'type': 'supergroup',
                'title': 'Test Group',
                'description': 'A test group'
            },
            {
                'id': -1009876543210,
                'type': 'channel',
                'title': 'Test Channel',
                'description': 'A test channel'
            }
        ]
        
        mock_member_count.side_effect = [50, 100]
        
        channels = self.service.fetch_channels()
        
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]['channel_type'], 'telegram_group')
        self.assertEqual(channels[0]['member_count'], 50)
        self.assertEqual(channels[1]['channel_type'], 'telegram_channel')
        self.assertEqual(channels[1]['member_count'], 100)
    
    @patch.object(TelegramService, 'validate_bot_token')
    def test_refresh_token_success(self, mock_validate):
        """Test successful token refresh (validation)."""
        mock_validate.return_value = {
            'valid': True,
            'bot_id': '123456789',
            'username': 'test_bot'
        }
        
        result = self.service.refresh_token()
        
        self.assertTrue(result)
        self.connection.refresh_from_db()
        self.assertEqual(self.connection.status, 'active')
    
    @patch.object(TelegramService, 'validate_bot_token')
    def test_refresh_token_failure(self, mock_validate):
        """Test failed token refresh."""
        mock_validate.return_value = {
            'valid': False,
            'error': 'Unauthorized'
        }
        
        result = self.service.refresh_token()
        
        self.assertFalse(result)
        self.connection.refresh_from_db()
        self.assertEqual(self.connection.status, 'error')
    
    def test_refresh_token_no_connection(self):
        """Test refresh fails without connection."""
        service = TelegramService()
        result = service.refresh_token()
        
        self.assertFalse(result)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_set_webhook_success(self, mock_api_request):
        """Test successful webhook setup."""
        mock_api_request.return_value = {
            'success': True,
            'result': True
        }
        
        result = self.service.set_webhook('bot_token', 'https://example.com/webhook')
        
        self.assertTrue(result)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_set_webhook_failure(self, mock_api_request):
        """Test failed webhook setup."""
        mock_api_request.return_value = {
            'success': False,
            'error': 'Invalid URL'
        }
        
        result = self.service.set_webhook('bot_token', 'invalid_url')
        
        self.assertFalse(result)
    
    @patch.object(TelegramService, '_make_api_request')
    def test_delete_webhook_success(self, mock_api_request):
        """Test successful webhook deletion."""
        mock_api_request.return_value = {
            'success': True,
            'result': True
        }
        
        result = self.service.delete_webhook('bot_token')
        
        self.assertTrue(result)


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob