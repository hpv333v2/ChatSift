"""
Tests for integrations app permissions.
"""
import logging
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from ..models import PlatformConnection, Channel
from ..permissions import IsEmailVerified, IsConnectionOwner, CanManageConnection

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class IsEmailVerifiedPermissionTest(TestCase):
    """Test cases for IsEmailVerified permission."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsEmailVerified()
        
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            username='verified',
            password='TestPass123!',
            email_verified=True
        )
        
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='TestPass123!',
            email_verified=False
        )
    
    def test_verified_user_has_permission(self):
        """Test that verified user has permission."""
        request = self.factory.get('/')
        request.user = self.verified_user
        
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_unverified_user_no_permission(self):
        """Test that unverified user does not have permission."""
        request = self.factory.get('/')
        request.user = self.unverified_user
        
        self.assertFalse(self.permission.has_permission(request, None))
    
    def test_unauthenticated_user_no_permission(self):
        """Test that unauthenticated user does not have permission."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        self.assertFalse(self.permission.has_permission(request, None))


class IsConnectionOwnerPermissionTest(TestCase):
    """Test cases for IsConnectionOwner permission."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsConnectionOwner()
        
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='TestPass123!'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='TestPass123!'
        )
        
        self.connection = PlatformConnection.objects.create(
            user=self.user1,
            platform='discord',
            platform_user_id='123456',
            platform_username='user1#1234',
            access_token='encrypted_token'
        )
        
        self.channel = Channel.objects.create(
            connection=self.connection,
            channel_id='789012',
            channel_name='general',
            channel_type='discord_channel'
        )
    
    def test_owner_has_permission_on_connection(self):
        """Test that connection owner has permission."""
        request = self.factory.get('/')
        request.user = self.user1
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.connection)
        )
    
    def test_non_owner_no_permission_on_connection(self):
        """Test that non-owner does not have permission."""
        request = self.factory.get('/')
        request.user = self.user2
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.connection)
        )
    
    def test_owner_has_permission_on_channel(self):
        """Test that connection owner has permission on channel."""
        request = self.factory.get('/')
        request.user = self.user1
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.channel)
        )
    
    def test_non_owner_no_permission_on_channel(self):
        """Test that non-owner does not have permission on channel."""
        request = self.factory.get('/')
        request.user = self.user2
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.channel)
        )


class CanManageConnectionPermissionTest(TestCase):
    """Test cases for CanManageConnection permission."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CanManageConnection()
        
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='TestPass123!'
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='TestPass123!'
        )
        
        self.active_connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='123456',
            platform_username='user#1234',
            access_token='encrypted_token',
            status='active'
        )
        
        self.error_connection = PlatformConnection.objects.create(
            user=self.user,
            platform='telegram',
            platform_user_id='789012',
            platform_username='user_bot',
            bot_token='encrypted_bot_token',
            status='error'
        )
        
        self.revoked_connection = PlatformConnection.objects.create(
            user=self.user,
            platform='discord',
            platform_user_id='345678',
            platform_username='user#5678',
            access_token='encrypted_token',
            status='revoked'
        )
    
    def test_owner_can_manage_active_connection(self):
        """Test that owner can manage active connection."""
        request = self.factory.patch('/')
        request.user = self.user
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.active_connection)
        )
    
    def test_owner_can_delete_error_connection(self):
        """Test that owner can delete error connection."""
        request = self.factory.delete('/')
        request.user = self.user
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.error_connection)
        )
    
    def test_owner_can_delete_revoked_connection(self):
        """Test that owner can delete revoked connection."""
        request = self.factory.delete('/')
        request.user = self.user
        
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.revoked_connection)
        )
    
    def test_owner_cannot_update_revoked_connection(self):
        """Test that owner cannot update revoked connection."""
        request = self.factory.patch('/')
        request.user = self.user
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.revoked_connection)
        )
    
    def test_non_owner_cannot_manage_connection(self):
        """Test that non-owner cannot manage connection."""
        request = self.factory.patch('/')
        request.user = self.other_user
        
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.active_connection)
        )


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob