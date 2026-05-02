import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedTextField

User = get_user_model()


class PlatformConnection(models.Model):
    """
    Stores user's platform connection credentials and metadata.
    Supports Discord and Telegram integrations.
    """
    
    PLATFORM_CHOICES = [
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='platform_connections'
    )
    platform = models.CharField(
        _('platform'),
        max_length=20,
        choices=PLATFORM_CHOICES
    )
    platform_user_id = models.CharField(
        _('platform user ID'),
        max_length=255,
        help_text=_('User ID from the platform (Discord user ID or Telegram user ID)')
    )
    platform_username = models.CharField(
        _('platform username'),
        max_length=255
    )
    
    # Encrypted credentials for OAuth (Discord)
    access_token = EncryptedTextField(
        _('access token'),
        help_text=_('OAuth access token (encrypted)')
    )
    refresh_token = EncryptedTextField(
        _('refresh token'),
        null=True,
        blank=True,
        help_text=_('OAuth refresh token (encrypted)')
    )
    token_expires_at = models.DateTimeField(
        _('token expires at'),
        null=True,
        blank=True,
        help_text=_('When the access token expires')
    )
    
    # Bot token for Telegram
    bot_token = EncryptedTextField(
        _('bot token'),
        null=True,
        blank=True,
        help_text=_('Telegram bot token (encrypted)')
    )
    
    # Connection status and metadata
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    last_sync = models.DateTimeField(
        _('last sync'),
        null=True,
        blank=True,
        help_text=_('Last time channels were synced')
    )
    error_message = models.TextField(
        _('error message'),
        null=True,
        blank=True,
        help_text=_('Last error message if status is error')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'platform_connections'
        verbose_name = _('Platform Connection')
        verbose_name_plural = _('Platform Connections')
        unique_together = [['user', 'platform', 'platform_user_id']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()} ({self.platform_username})"
    
    def is_token_expired(self):
        """Check if the access token is expired."""
        if not self.token_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() >= self.token_expires_at
    
    def mark_as_error(self, error_message):
        """Mark connection as error with message."""
        self.status = 'error'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def mark_as_active(self):
        """Mark connection as active and clear error."""
        self.status = 'active'
        self.error_message = None
        self.save(update_fields=['status', 'error_message', 'updated_at'])


class Channel(models.Model):
    """
    Stores available channels/servers from connected platforms.
    Represents Discord servers/channels or Telegram groups/channels.
    """
    
    CHANNEL_TYPE_CHOICES = [
        ('discord_server', 'Discord Server'),
        ('discord_channel', 'Discord Channel'),
        ('telegram_group', 'Telegram Group'),
        ('telegram_channel', 'Telegram Channel'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    connection = models.ForeignKey(
        PlatformConnection,
        on_delete=models.CASCADE,
        related_name='channels'
    )
    
    # Channel identification
    channel_id = models.CharField(
        _('channel ID'),
        max_length=255,
        help_text=_('Platform-specific channel/server ID')
    )
    channel_name = models.CharField(
        _('channel name'),
        max_length=255
    )
    channel_type = models.CharField(
        _('channel type'),
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES
    )
    
    # Additional metadata
    member_count = models.IntegerField(
        _('member count'),
        null=True,
        blank=True,
        help_text=_('Number of members in the channel/server')
    )
    icon_url = models.URLField(
        _('icon URL'),
        max_length=500,
        null=True,
        blank=True,
        help_text=_('URL to channel/server icon')
    )
    description = models.TextField(
        _('description'),
        null=True,
        blank=True,
        help_text=_('Channel/server description')
    )
    
    # Permissions
    can_read_messages = models.BooleanField(
        _('can read messages'),
        default=False,
        help_text=_('Whether bot has permission to read messages')
    )
    can_read_history = models.BooleanField(
        _('can read history'),
        default=False,
        help_text=_('Whether bot can read message history')
    )
    
    # Status
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this channel is still accessible')
    )
    last_synced = models.DateTimeField(
        _('last synced'),
        null=True,
        blank=True,
        help_text=_('Last time channel data was synced')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'channels'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        unique_together = [['connection', 'channel_id']]
        ordering = ['channel_name']
        indexes = [
            models.Index(fields=['connection', 'is_active']),
            models.Index(fields=['channel_type']),
        ]
    
    def __str__(self):
        return f"{self.channel_name} ({self.get_channel_type_display()})"
    
    @property
    def platform(self):
        """Get the platform this channel belongs to."""
        return self.connection.platform
    
    def mark_inactive(self):
        """Mark channel as inactive (no longer accessible)."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def update_sync_time(self):
        """Update the last synced timestamp."""
        from django.utils import timezone
        self.last_synced = timezone.now()
        self.save(update_fields=['last_synced', 'updated_at'])


# Made with Bob