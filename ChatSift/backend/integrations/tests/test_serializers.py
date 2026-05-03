"""
Tests for integrations app serializers.
"""
import logging
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import PlatformConnection, Channel
from ..serializers import (
    ChannelSerializer,
    PlatformConnectionSerializer,
    PlatformConnectionDetailSerializer,
    DiscordConnectionSerializer,
    TelegramConnectionSerializer,
)

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class ChannelSerializerTest(TestCase):
    """Test cases for ChannelSerializer."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='encrypted_token'
        )
        
        self.channel = Channel.objects.create(
            connection=self.connection,
            channel_id='789012',
            channel_name='general',
            channel_type='discord_channel',
            member_count=100,
            can_read_messages=True
        )
    
    def test_channel_serialization(self):
        """Test channel serialization includes all fields."""
        serializer = ChannelSerializer(self.channel)
        data = serializer.data
        
        self.assertEqual(data['channel_name'], 'general')
        self.assertEqual(data['channel_type'], 'discord_channel')
        self.assertEqual(data['platform'], 'discord')
        self.assertEqual(data['member_count'], 100)
        self.assertTrue(data['can_read_messages'])
    
    def test_channel_read_only_fields(self):
        """Test that read-only fields cannot be updated."""
        data = {
            'channel_id': 'new_id',
            'member_count': 200,
        }
        serializer = ChannelSerializer(self.channel, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())
        # Read-only fields should not be updated
        serializer.save()
        self.channel.refresh_from_db()
        self.assertEqual(self.channel.channel_id, '789012')  # Unchanged
        self.assertEqual(self.channel.member_count, 100)  # Unchanged


class PlatformConnectionSerializerTest(TestCase):
    """Test cases for PlatformConnectionSerializer."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='testuser#1234',
            access_token='encrypted_token',
            status='active'
        )
        
        # Create some channels
        for i in range(3):
            Channel.objects.create(
                connection=self.connection,
                channel_id=f'channel_{i}',
                channel_name=f'Channel {i}',
                channel_type='discord_channel'
            )
    
    def test_connection_serialization(self):
        """Test connection serialization includes all fields."""
        serializer = PlatformConnectionSerializer(self.connection)
        data = serializer.data
        
        self.assertEqual(data['platform'], 'discord')
        self.assertEqual(data['platform_display'], 'Discord')
        self.assertEqual(data['platform_username'], 'testuser#1234')
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['status_display'], 'Active')
        self.assertEqual(data['channels_count'], 3)
        self.assertFalse(data['is_token_expired'])
    
    def test_connection_detail_includes_channels(self):
        """Test detailed serializer includes channels."""
        serializer = PlatformConnectionDetailSerializer(self.connection)
        data = serializer.data
        
        self.assertIn('channels', data)
        self.assertEqual(len(data['channels']), 3)
        self.assertEqual(data['channels'][0]['channel_name'], 'Channel 0')


class DiscordConnectionSerializerTest(TestCase):
    """Test cases for DiscordConnectionSerializer."""
    
    def test_valid_discord_callback_data(self):
        """Test validation of valid Discord callback data."""
        data = {
            'code': 'authorization_code_here',
            'state': 'state_token_here'
        }
        serializer = DiscordConnectionSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['code'], 'authorization_code_here')
        self.assertEqual(serializer.validated_data['state'], 'state_token_here')
    
    def test_missing_code(self):
        """Test validation fails when code is missing."""
        data = {'state': 'state_token_here'}
        serializer = DiscordConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_missing_state(self):
        """Test validation fails when state is missing."""
        data = {'code': 'authorization_code_here'}
        serializer = DiscordConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('state', serializer.errors)


class TelegramConnectionSerializerTest(TestCase):
    """Test cases for TelegramConnectionSerializer."""
    
    def test_valid_bot_token(self):
        """Test validation of valid Telegram bot token."""
        data = {'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}
        serializer = TelegramConnectionSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['bot_token'],
            '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
        )
    
    def test_invalid_bot_token_no_separator(self):
        """Test validation fails for token without separator."""
        data = {'bot_token': 'invalid_token_without_separator'}
        serializer = TelegramConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('bot_token', serializer.errors)
    
    def test_invalid_bot_token_non_numeric_id(self):
        """Test validation fails for token with non-numeric bot ID."""
        data = {'bot_token': 'abc:DEF1234ghIkl-zyx57W2v1u123ew11'}
        serializer = TelegramConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('bot_token', serializer.errors)
    
    def test_bot_token_too_short(self):
        """Test validation fails for token that's too short."""
        data = {'bot_token': '123:ABC'}
        serializer = TelegramConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('bot_token', serializer.errors)
    
    def test_missing_bot_token(self):
        """Test validation fails when bot_token is missing."""
        data = {}
        serializer = TelegramConnectionSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('bot_token', serializer.errors)


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob