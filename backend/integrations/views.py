"""
API views for the integrations app.
"""
import logging
import secrets
from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import PlatformConnection, Channel
from .serializers import (
    PlatformConnectionSerializer,
    PlatformConnectionDetailSerializer,
    ChannelSerializer,
    DiscordConnectionSerializer,
    TelegramConnectionSerializer,
    ConnectionRefreshSerializer,
)
from .permissions import IsEmailVerified, IsConnectionOwner, CanManageConnection
from .services import DiscordService, TelegramService

User = get_user_model()
logger = logging.getLogger(__name__)


class DiscordAuthorizeView(views.APIView):
    """
    Initiate Discord OAuth flow.
    
    GET /api/v1/integrations/discord/authorize/
    """
    permission_classes = [IsAuthenticated, IsEmailVerified]
    
    def get(self, request):
        """Generate Discord OAuth authorization URL."""
        try:
            # Generate state token for CSRF protection
            state = secrets.token_urlsafe(32)
            request.session['discord_oauth_state'] = state
            request.session['discord_oauth_timestamp'] = timezone.now().isoformat()
            
            # Generate authorization URL
            discord_service = DiscordService()
            auth_data = discord_service.generate_authorization_url(state)
            
            return Response({
                'status': 'success',
                'data': {
                    'authorization_url': auth_data['url']
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating Discord auth URL: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'Failed to generate authorization URL'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiscordCallbackView(views.APIView):
    """
    Handle Discord OAuth callback.
    
    GET /api/v1/integrations/discord/callback/?code={code}&state={state}
    """
    permission_classes = [IsAuthenticated, IsEmailVerified]
    
    def get(self, request):
        """Process Discord OAuth callback."""
        serializer = DiscordConnectionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        state = serializer.validated_data['state']
        
        # Verify state token
        session_state = request.session.get('discord_oauth_state')
        if not session_state or session_state != state:
            return Response({
                'status': 'error',
                'message': 'Invalid state parameter. Possible CSRF attack.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check state timestamp (expire after 10 minutes)
        state_timestamp = request.session.get('discord_oauth_timestamp')
        if state_timestamp:
            from dateutil import parser
            timestamp = parser.isoparse(state_timestamp)
            if timezone.now() - timestamp > timedelta(minutes=10):
                return Response({
                    'status': 'error',
                    'message': 'Authorization expired. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            discord_service = DiscordService()
            
            # Exchange code for token
            token_result = discord_service.exchange_code_for_token(code)
            if not token_result.get('success'):
                return Response({
                    'status': 'error',
                    'message': token_result.get('error', 'Failed to exchange code for token')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user information
            user_result = discord_service.get_current_user(token_result['access_token'])
            if not user_result.get('success'):
                return Response({
                    'status': 'error',
                    'message': user_result.get('error', 'Failed to get user information')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if connection already exists
            existing_connection = PlatformConnection.objects.filter(
                user=request.user,
                platform='discord',
                platform_user_id=user_result['user_id']
            ).first()
            
            if existing_connection:
                # Update existing connection
                connection = existing_connection
                connection.access_token = token_result['access_token']
                connection.refresh_token = token_result.get('refresh_token')
                connection.token_expires_at = timezone.now() + timedelta(seconds=token_result['expires_in'])
                connection.platform_username = user_result['username']
                connection.status = 'active'
                connection.error_message = None
                connection.save()
            else:
                # Create new connection
                connection = PlatformConnection.objects.create(
                    user=request.user,
                    platform='discord',
                    platform_user_id=user_result['user_id'],
                    platform_username=user_result['username'],
                    access_token=token_result['access_token'],
                    refresh_token=token_result.get('refresh_token'),
                    token_expires_at=timezone.now() + timedelta(seconds=token_result['expires_in']),
                    status='active'
                )
            
            # Sync channels in background (for now, do it synchronously)
            discord_service_with_connection = DiscordService(connection)
            sync_result = discord_service_with_connection.sync_channels()
            
            # Clear session state
            request.session.pop('discord_oauth_state', None)
            request.session.pop('discord_oauth_timestamp', None)
            
            serializer = PlatformConnectionSerializer(connection)
            return Response({
                'status': 'success',
                'data': serializer.data,
                'message': 'Discord connected successfully'
            }, status=status.HTTP_201_CREATED if not existing_connection else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing Discord callback: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'Failed to connect Discord account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TelegramConnectView(views.APIView):
    """
    Connect Telegram bot.
    
    POST /api/v1/integrations/telegram/connect/
    """
    permission_classes = [IsAuthenticated, IsEmailVerified]
    
    def post(self, request):
        """Connect Telegram bot using bot token."""
        serializer = TelegramConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        bot_token = serializer.validated_data['bot_token']
        
        try:
            telegram_service = TelegramService()
            
            # Validate bot token
            validation_result = telegram_service.validate_bot_token(bot_token)
            if not validation_result.get('valid'):
                return Response({
                    'status': 'error',
                    'message': validation_result.get('error', 'Invalid bot token')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if connection already exists
            existing_connection = PlatformConnection.objects.filter(
                user=request.user,
                platform='telegram',
                platform_user_id=validation_result['bot_id']
            ).first()
            
            if existing_connection:
                # Update existing connection
                connection = existing_connection
                connection.bot_token = bot_token
                connection.platform_username = validation_result['username']
                connection.status = 'active'
                connection.error_message = None
                connection.save()
            else:
                # Create new connection
                connection = PlatformConnection.objects.create(
                    user=request.user,
                    platform='telegram',
                    platform_user_id=validation_result['bot_id'],
                    platform_username=validation_result['username'],
                    bot_token=bot_token,
                    status='active'
                )
            
            # Sync channels
            telegram_service_with_connection = TelegramService(connection)
            sync_result = telegram_service_with_connection.sync_channels()
            
            serializer = PlatformConnectionSerializer(connection)
            return Response({
                'status': 'success',
                'data': serializer.data,
                'message': 'Telegram bot connected successfully'
            }, status=status.HTTP_201_CREATED if not existing_connection else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error connecting Telegram bot: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'Failed to connect Telegram bot'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConnectionListView(generics.ListAPIView):
    """
    List all platform connections for the authenticated user.
    
    GET /api/v1/integrations/
    """
    serializer_class = PlatformConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return connections for the current user."""
        return PlatformConnection.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """List connections with custom response format."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'data': {
                'connections': serializer.data
            }
        }, status=status.HTTP_200_OK)


class ConnectionDetailView(generics.RetrieveDestroyAPIView):
    """
    Get or delete a specific platform connection.
    
    GET /api/v1/integrations/{id}/
    DELETE /api/v1/integrations/{id}/
    """
    serializer_class = PlatformConnectionDetailSerializer
    permission_classes = [IsAuthenticated, IsConnectionOwner]
    
    def get_queryset(self):
        """Return connections for the current user."""
        return PlatformConnection.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Get connection details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Delete connection."""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'status': 'success',
            'message': 'Connection deleted successfully'
        }, status=status.HTTP_200_OK)


class ConnectionRefreshView(views.APIView):
    """
    Refresh a platform connection and sync channels.
    
    POST /api/v1/integrations/{pk}/refresh/
    """
    permission_classes = [IsAuthenticated, IsConnectionOwner]
    
    def post(self, request, pk):
        """Refresh connection and sync channels."""
        try:
            connection = PlatformConnection.objects.get(pk=pk, user=request.user)
        except PlatformConnection.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Connection not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Get appropriate service
            if connection.platform == 'discord':
                service = DiscordService(connection)
            elif connection.platform == 'telegram':
                service = TelegramService(connection)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Unsupported platform'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Refresh token if needed
            if connection.platform == 'discord' and connection.is_token_expired():
                refresh_success = service.refresh_token()
                if not refresh_success:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to refresh token'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Sync channels
            sync_result = service.sync_channels()
            
            if not sync_result.get('success'):
                return Response({
                    'status': 'error',
                    'message': sync_result.get('error', 'Failed to sync channels')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Prepare response
            response_data = ConnectionRefreshSerializer({
                'channels_synced': sync_result['channels_synced'],
                'channels_added': sync_result.get('channels_added', 0),
                'channels_removed': sync_result.get('channels_removed', 0),
                'last_sync': connection.last_sync
            }).data
            
            return Response({
                'status': 'success',
                'data': response_data,
                'message': 'Connection refreshed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error refreshing connection: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'Failed to refresh connection'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Made with Bob