import logging
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .tokens import generate_verification_token, verify_token

User = get_user_model()

# Disable logging during tests
logging.disable(logging.CRITICAL)


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.email_verified)
    
    def test_user_profile_created_on_user_creation(self):
        """Test that UserProfile is automatically created when User is created."""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_user_str_method(self):
        """Test User __str__ method returns email."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)


class UserRegistrationAPITest(APITestCase):
    """Test cases for user registration API."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
    
    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('tokens', response.data['data'])
        self.assertIn('user', response.data['data'])
    
    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = self.valid_data.copy()
        data['password_confirm'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            email=self.valid_data['email'],
            username='otheruser',
            password='Pass123!'
        )
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_user_weak_password(self):
        """Test registration fails with weak password."""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITest(APITestCase):
    """Test cases for user login API."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('tokens', response.data['data'])
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_inactive_user(self):
        """Test login fails for inactive user."""
        self.user.is_active = False
        self.user.save()
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutAPITest(APITestCase):
    """Test cases for user logout API."""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = '/api/v1/auth/logout/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_logout_success(self):
        """Test successful logout."""
        data = {'refresh': str(self.refresh)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    def test_logout_missing_token(self):
        """Test logout fails without refresh token."""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_invalid_token(self):
        """Test logout fails with invalid token."""
        data = {'refresh': 'invalid-token'}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CurrentUserAPITest(APITestCase):
    """Test cases for current user profile API."""
    
    def setUp(self):
        self.client = APIClient()
        self.me_url = '/api/v1/users/me/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_get_current_user(self):
        """Test retrieving current user profile."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.user.email)
    
    def test_update_current_user(self):
        """Test updating current user profile."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.me_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_delete_current_user(self):
        """Test soft deleting current user account."""
        response = self.client.delete(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class EmailVerificationTokenTest(TestCase):
    """Test cases for email verification token generation and validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
    
    def test_generate_verification_token(self):
        """Test generating verification token."""
        token_data = generate_verification_token(self.user)
        self.assertIn('token', token_data)
        self.assertIn('uid', token_data)
    
    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        token_data = generate_verification_token(self.user)
        verified_user = verify_token(token_data['uid'], token_data['token'])
        self.assertEqual(verified_user, self.user)
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        token_data = generate_verification_token(self.user)
        verified_user = verify_token(token_data['uid'], 'invalid-token')
        self.assertIsNone(verified_user)
    
    def test_token_invalid_after_verification(self):
        """Test token becomes invalid after email is verified."""
        token_data = generate_verification_token(self.user)
        
        # Verify email
        self.user.email_verified = True
        self.user.save()
        
        # Token should now be invalid
        verified_user = verify_token(token_data['uid'], token_data['token'])
        self.assertIsNone(verified_user)


class EmailVerificationAPITest(APITestCase):
    """Test cases for email verification API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.send_url = '/api/v1/auth/email/verify/send/'
        self.confirm_url = '/api/v1/auth/email/verify/confirm/'
        self.status_url = '/api/v1/auth/email/status/'
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_send_verification_email(self):
        """Test sending verification email."""
        response = self.client.post(self.send_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_send_verification_already_verified(self):
        """Test sending verification email when already verified."""
        self.user.email_verified = True
        self.user.save()
        response = self.client.post(self.send_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already verified', response.data['message'])
    
    def test_verify_email_success(self):
        """Test successful email verification."""
        token_data = generate_verification_token(self.user)
        response = self.client.post(self.confirm_url, token_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
    
    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        data = {'token': 'invalid', 'uid': 'invalid'}
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_email_verification_status(self):
        """Test checking email verification status."""
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['data']['email_verified'])


# Re-enable logging after tests
logging.disable(logging.NOTSET)

# Made with Bob
