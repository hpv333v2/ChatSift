"""
Serializers for the integrations app.
"""
from rest_framework import serializers
from .models import PlatformConnection, Channel


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for Channel model."""
    
    platform = serializers.CharField(source='connection.platform', read_only=True)
    
    class Meta:
        model = Channel
        fields = [
            'id',
            'channel_id',
            'channel_name',
            'channel_type',
            'platform',
            'member_count',
            'icon_url',
            'description',
            'can_read_messages',
            'can_read_history',
            'is_active',
            'last_synced',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'channel_id',
            'platform',
            'member_count',
            'icon_url',
            'description',
            'can_read_messages',
            'can_read_history',
            'last_synced',
            'created_at',
        ]


class PlatformConnectionSerializer(serializers.ModelSerializer):
    """Serializer for PlatformConnection model."""
    
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    channels_count = serializers.SerializerMethodField()
    is_token_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = PlatformConnection
        fields = [
            'id',
            'platform',
            'platform_display',
            'platform_user_id',
            'platform_username',
            'status',
            'status_display',
            'is_token_expired',
            'last_sync',
            'error_message',
            'channels_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'platform',
            'platform_user_id',
            'platform_username',
            'status',
            'is_token_expired',
            'last_sync',
            'error_message',
            'channels_count',
            'created_at',
            'updated_at',
        ]
    
    def get_channels_count(self, obj):
        """Get count of active channels for this connection."""
        return obj.channels.filter(is_active=True).count()
    
    def get_is_token_expired(self, obj):
        """Check if the connection token is expired."""
        return obj.is_token_expired()


class PlatformConnectionDetailSerializer(PlatformConnectionSerializer):
    """Detailed serializer for PlatformConnection with channels."""
    
    channels = ChannelSerializer(many=True, read_only=True)
    
    class Meta(PlatformConnectionSerializer.Meta):
        fields = PlatformConnectionSerializer.Meta.fields + ['channels']


class DiscordConnectionSerializer(serializers.Serializer):
    """Serializer for Discord OAuth callback data."""
    
    code = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate OAuth callback data."""
        # State validation will be done in the view against session
        return attrs


class TelegramConnectionSerializer(serializers.Serializer):
    """Serializer for Telegram bot connection."""
    
    bot_token = serializers.CharField(
        required=True,
        min_length=40,
        max_length=50,
        help_text="Telegram bot token from @BotFather"
    )
    
    def validate_bot_token(self, value):
        """Validate bot token format."""
        # Basic format validation: should be like "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        if ':' not in value:
            raise serializers.ValidationError(
                "Invalid bot token format. Token should contain ':' separator."
            )
        
        parts = value.split(':', 1)
        if not parts[0].isdigit():
            raise serializers.ValidationError(
                "Invalid bot token format. First part should be numeric bot ID."
            )
        
        return value


class ConnectionRefreshSerializer(serializers.Serializer):
    """Serializer for connection refresh response."""
    
    channels_synced = serializers.IntegerField()
    channels_added = serializers.IntegerField(default=0)
    channels_removed = serializers.IntegerField(default=0)
    last_sync = serializers.DateTimeField()


class DiscordServerSerializer(serializers.Serializer):
    """Serializer for Discord server data."""
    
    id = serializers.UUIDField(read_only=True)
    server_id = serializers.CharField()
    name = serializers.CharField()
    icon_url = serializers.URLField(allow_null=True)
    member_count = serializers.IntegerField(allow_null=True)
    channels = ChannelSerializer(many=True, read_only=True)


class TelegramGroupSerializer(serializers.Serializer):
    """Serializer for Telegram group data."""
    
    id = serializers.UUIDField(read_only=True)
    channel_id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.CharField()
    member_count = serializers.IntegerField(allow_null=True)
    can_read_messages = serializers.BooleanField()


# Made with Bob