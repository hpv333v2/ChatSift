from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsOwner

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/v1/auth/register/
    
    Request body:
    {
        "email": "user@example.com",
        "username": "johndoe",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "first_name": "John",  # optional
        "last_name": "Doe"  # optional
    }
    
    Response (201 Created):
    {
        "status": "success",
        "data": {
            "user": {...},
            "tokens": {
                "access": "...",
                "refresh": "..."
            }
        },
        "message": "User registered successfully"
    }
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'status': 'success',
            'data': serializer.to_representation(user),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(views.APIView):
    """
    API endpoint for user login.
    
    POST /api/v1/auth/login/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    Response (200 OK):
    {
        "status": "success",
        "data": {
            "user": {...},
            "tokens": {
                "access": "...",
                "refresh": "..."
            }
        },
        "message": "Login successful"
    }
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(views.APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    
    POST /api/v1/auth/logout/
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    
    Response (200 OK):
    {
        "status": "success",
        "message": "Logout successful"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'status': 'error',
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'status': 'success',
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """
    API endpoint for refreshing JWT tokens.
    
    POST /api/v1/auth/refresh/
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    
    Response (200 OK):
    {
        "access": "new_access_token",
        "refresh": "new_refresh_token"  # if rotation is enabled
    }
    """
    pass


class CurrentUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for current user profile management.
    
    GET /api/v1/users/me/
    - Get current user profile
    
    PATCH /api/v1/users/me/
    - Update current user profile
    
    DELETE /api/v1/users/me/
    - Delete current user account
    """
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get current user profile."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update current user profile."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'data': UserSerializer(instance).data,
            'message': 'Profile updated successfully'
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Delete current user account (soft delete)."""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'status': 'success',
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)

# Made with Bob



class SendVerificationEmailView(views.APIView):
    """
    API endpoint to send/resend email verification link.
    
    POST /api/v1/auth/email/verify/send/
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response (200 OK):
    {
        "status": "success",
        "message": "Verification email sent to user@example.com"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if already verified
        if user.email_verified:
            return Response({
                'status': 'info',
                'message': 'Email is already verified'
            }, status=status.HTTP_200_OK)
        
        # Send verification email
        from .utils import send_verification_email
        email_sent = send_verification_email(user, request)
        
        if email_sent:
            return Response({
                'status': 'success',
                'message': f'Verification email sent to {user.email}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to send verification email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(views.APIView):
    """
    API endpoint to verify email with token.
    
    POST /api/v1/auth/email/verify/confirm/
    
    Request body:
    {
        "token": "verification-token",
        "uid": "user-id-base64"
    }
    
    Response (200 OK):
    {
        "status": "success",
        "message": "Email verified successfully",
        "data": {
            "email_verified": true,
            "email_verified_at": "2026-05-02T12:30:00Z"
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        from .serializers import EmailVerificationSerializer
        from .tokens import verify_token
        from .utils import send_welcome_email
        
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        
        # Verify token and get user
        user = verify_token(uid, token)
        
        if not user:
            return Response({
                'status': 'error',
                'message': 'Invalid or expired verification link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already verified
        if user.email_verified:
            return Response({
                'status': 'info',
                'message': 'Email is already verified'
            }, status=status.HTTP_200_OK)
        
        # Mark email as verified
        user.email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=['email_verified', 'email_verified_at'])
        
        # Send welcome email
        send_welcome_email(user)
        
        return Response({
            'status': 'success',
            'message': 'Email verified successfully',
            'data': {
                'email_verified': True,
                'email_verified_at': user.email_verified_at
            }
        }, status=status.HTTP_200_OK)


class EmailVerificationStatusView(views.APIView):
    """
    API endpoint to check email verification status.
    
    GET /api/v1/auth/email/status/
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response (200 OK):
    {
        "status": "success",
        "data": {
            "email": "user@example.com",
            "email_verified": false,
            "can_create_integrations": false
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        return Response({
            'status': 'success',
            'data': {
                'email': user.email,
                'email_verified': user.email_verified,
                'email_verified_at': user.email_verified_at,
                'can_create_integrations': user.email_verified
            }
        }, status=status.HTTP_200_OK)
