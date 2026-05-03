from django.contrib import admin
from .models import PlatformConnection, Channel


@admin.register(PlatformConnection)
class PlatformConnectionAdmin(admin.ModelAdmin):
    """Admin interface for PlatformConnection model."""
    
    list_display = [
        'user',
        'platform',
        'platform_username',
        'status',
        'created_at',
        'last_sync'
    ]
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['user__email', 'platform_username', 'platform_user_id']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'access_token',
        'refresh_token',
        'bot_token'
    ]
    
    fieldsets = (
        ('Connection Info', {
            'fields': ('id', 'user', 'platform', 'platform_user_id', 'platform_username')
        }),
        ('Credentials (Encrypted)', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at', 'bot_token'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'last_sync')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin interface for Channel model."""
    
    list_display = [
        'channel_name',
        'channel_type',
        'connection',
        'member_count',
        'is_active',
        'can_read_messages',
        'last_synced'
    ]
    list_filter = ['channel_type', 'is_active', 'can_read_messages', 'created_at']
    search_fields = ['channel_name', 'channel_id', 'connection__platform_username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Channel Info', {
            'fields': ('id', 'connection', 'channel_id', 'channel_name', 'channel_type')
        }),
        ('Metadata', {
            'fields': ('member_count', 'icon_url', 'description')
        }),
        ('Permissions', {
            'fields': ('can_read_messages', 'can_read_history')
        }),
        ('Status', {
            'fields': ('is_active', 'last_synced')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False


# Made with Bob