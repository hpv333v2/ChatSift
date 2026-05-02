# 📋 Integrations APIs - Requirements & Specifications

## 🎯 Overview
The Integrations module enables users to connect their Discord and Telegram accounts to ChatSift, allowing the platform to monitor and summarize conversations from these platforms.

## ✅ Core Requirements

### 1. Supported Platforms
- **Discord** - OAuth2 integration for server access
- **Telegram** - Bot token-based integration for group access

### 2. Security Requirements
- ✅ Email verification required before creating integrations
- ✅ Encrypted storage of OAuth tokens and credentials
- ✅ Secure token refresh mechanisms
- ✅ Rate limiting on API calls
- ✅ Audit logging for integration actions

### 3. User Experience
- Simple connection flow for each platform
- Clear error messages for failed connections
- Ability to reconnect/refresh credentials
- View connected platforms and their status
- Disconnect platforms when needed

## 🗄️ Database Schema

### PlatformConnection Model
```python
class PlatformConnection(models.Model):
    """Stores user's platform connection credentials."""
    
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
    
    id = UUIDField(primary_key=True)
    user = ForeignKey(User, on_delete=CASCADE)
    platform = CharField(choices=PLATFORM_CHOICES)
    platform_user_id = CharField()  # Discord user ID or Telegram user ID
    platform_username = CharField()
    
    # Encrypted credentials
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField(null=True)
    token_expires_at = DateTimeField(null=True)
    
    # Bot token for Telegram
    bot_token = EncryptedTextField(null=True)
    
    status = CharField(choices=STATUS_CHOICES, default='active')
    last_sync = DateTimeField(null=True)
    error_message = TextField(null=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'platform', 'platform_user_id']]
```

### Channel Model
```python
class Channel(models.Model):
    """Stores available channels/servers from connected platforms."""
    
    CHANNEL_TYPE_CHOICES = [
        ('discord_server', 'Discord Server'),
        ('discord_channel', 'Discord Channel'),
        ('telegram_group', 'Telegram Group'),
        ('telegram_channel', 'Telegram Channel'),
    ]
    
    id = UUIDField(primary_key=True)
    connection = ForeignKey(PlatformConnection, on_delete=CASCADE)
    
    channel_id = CharField()  # Platform-specific channel/server ID
    channel_name = CharField()
    channel_type = CharField(choices=CHANNEL_TYPE_CHOICES)
    
    # Additional metadata
    member_count = IntegerField(null=True)
    icon_url = URLField(null=True)
    description = TextField(null=True)
    
    # Permissions
    can_read_messages = BooleanField(default=False)
    can_read_history = BooleanField(default=False)
    
    is_active = BooleanField(default=True)
    last_synced = DateTimeField(null=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['connection', 'channel_id']]
```

## 🔌 API Endpoints

### Discord Integration

#### 1. Initiate Discord OAuth
```
GET /api/v1/integrations/discord/authorize/
```
**Description:** Redirects user to Discord OAuth consent page

**Response:**
```json
{
    "status": "success",
    "data": {
        "authorization_url": "https://discord.com/api/oauth2/authorize?..."
    }
}
```

#### 2. Discord OAuth Callback
```
GET /api/v1/integrations/discord/callback/?code={code}&state={state}
```
**Description:** Handles OAuth callback from Discord

**Response:**
```json
{
    "status": "success",
    "data": {
        "connection_id": "uuid",
        "platform": "discord",
        "username": "User#1234",
        "servers_count": 5
    },
    "message": "Discord connected successfully"
}
```

#### 3. List Discord Servers
```
GET /api/v1/integrations/discord/{connection_id}/servers/
```
**Description:** Lists all Discord servers the user has access to

**Response:**
```json
{
    "status": "success",
    "data": {
        "servers": [
            {
                "id": "uuid",
                "server_id": "123456789",
                "name": "My Server",
                "icon_url": "https://...",
                "member_count": 150,
                "channels": [
                    {
                        "id": "uuid",
                        "channel_id": "987654321",
                        "name": "general",
                        "type": "discord_channel",
                        "can_read_messages": true
                    }
                ]
            }
        ]
    }
}
```

### Telegram Integration

#### 1. Connect Telegram Bot
```
POST /api/v1/integrations/telegram/connect/
```
**Description:** Connects Telegram using bot token

**Request:**
```json
{
    "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "connection_id": "uuid",
        "platform": "telegram",
        "bot_username": "my_bot",
        "bot_name": "My Bot"
    },
    "message": "Telegram bot connected successfully"
}
```

#### 2. List Telegram Groups
```
GET /api/v1/integrations/telegram/{connection_id}/groups/
```
**Description:** Lists all Telegram groups the bot has access to

**Response:**
```json
{
    "status": "success",
    "data": {
        "groups": [
            {
                "id": "uuid",
                "channel_id": "-1001234567890",
                "name": "My Group",
                "type": "telegram_group",
                "member_count": 50,
                "can_read_messages": true
            }
        ]
    }
}
```

### General Integration Endpoints

#### 1. List All Connections
```
GET /api/v1/integrations/
```
**Description:** Lists all platform connections for the authenticated user

**Response:**
```json
{
    "status": "success",
    "data": {
        "connections": [
            {
                "id": "uuid",
                "platform": "discord",
                "username": "User#1234",
                "status": "active",
                "connected_at": "2026-05-02T10:00:00Z",
                "servers_count": 5,
                "channels_count": 15
            },
            {
                "id": "uuid",
                "platform": "telegram",
                "username": "my_bot",
                "status": "active",
                "connected_at": "2026-05-02T11:00:00Z",
                "groups_count": 3
            }
        ]
    }
}
```

#### 2. Get Connection Details
```
GET /api/v1/integrations/{connection_id}/
```
**Description:** Get detailed information about a specific connection

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": "uuid",
        "platform": "discord",
        "username": "User#1234",
        "status": "active",
        "connected_at": "2026-05-02T10:00:00Z",
        "last_sync": "2026-05-02T12:00:00Z",
        "channels": [...]
    }
}
```

#### 3. Refresh Connection
```
POST /api/v1/integrations/{connection_id}/refresh/
```
**Description:** Refreshes the connection and syncs channels

**Response:**
```json
{
    "status": "success",
    "message": "Connection refreshed successfully",
    "data": {
        "channels_synced": 15,
        "last_sync": "2026-05-02T12:30:00Z"
    }
}
```

#### 4. Disconnect Platform
```
DELETE /api/v1/integrations/{connection_id}/
```
**Description:** Disconnects and removes the platform connection

**Response:**
```json
{
    "status": "success",
    "message": "Platform disconnected successfully"
}
```

## 🔐 Permissions

### IsEmailVerified Permission
```python
class IsEmailVerified(BasePermission):
    """
    Ensures user has verified their email before creating integrations.
    """
    message = "Email verification required to connect platforms."
    
    def has_permission(self, request, view):
        return request.user.email_verified
```

### IsConnectionOwner Permission
```python
class IsConnectionOwner(BasePermission):
    """
    Ensures user owns the platform connection.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

## 🔄 Integration Flow

### Discord Flow
1. User clicks "Connect Discord"
2. Backend generates OAuth URL with state parameter
3. User authorizes on Discord
4. Discord redirects to callback URL with code
5. Backend exchanges code for access token
6. Backend fetches user's servers and channels
7. Backend stores connection and channel data
8. User can now select channels to monitor

### Telegram Flow
1. User creates a Telegram bot via @BotFather
2. User copies bot token
3. User pastes token in ChatSift
4. Backend validates token with Telegram API
5. Backend stores bot connection
6. User adds bot to desired groups
7. Backend fetches group list
8. User can now select groups to monitor

## 📊 Error Handling

### Common Error Responses

#### Invalid Token
```json
{
    "status": "error",
    "message": "Invalid or expired token",
    "code": "INVALID_TOKEN"
}
```

#### Email Not Verified
```json
{
    "status": "error",
    "message": "Email verification required to connect platforms",
    "code": "EMAIL_NOT_VERIFIED"
}
```

#### Platform API Error
```json
{
    "status": "error",
    "message": "Failed to connect to Discord API",
    "code": "PLATFORM_API_ERROR",
    "details": "Rate limit exceeded"
}
```

#### Connection Already Exists
```json
{
    "status": "error",
    "message": "This platform account is already connected",
    "code": "CONNECTION_EXISTS"
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Discord OAuth
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/api/v1/integrations/discord/callback/

# Telegram
TELEGRAM_BOT_API_URL=https://api.telegram.org

# Encryption
FIELD_ENCRYPTION_KEY=your_encryption_key_here
```

### Django Settings
```python
# Integrations Configuration
INTEGRATIONS = {
    'DISCORD': {
        'CLIENT_ID': config('DISCORD_CLIENT_ID'),
        'CLIENT_SECRET': config('DISCORD_CLIENT_SECRET'),
        'REDIRECT_URI': config('DISCORD_REDIRECT_URI'),
        'SCOPES': ['identify', 'guilds', 'guilds.members.read'],
        'API_VERSION': 'v10',
    },
    'TELEGRAM': {
        'API_URL': config('TELEGRAM_BOT_API_URL', default='https://api.telegram.org'),
        'TIMEOUT': 30,
    },
    'TOKEN_REFRESH_THRESHOLD': 3600,  # Refresh tokens 1 hour before expiry
    'SYNC_INTERVAL': 3600,  # Sync channels every hour
}
```

## 📦 Dependencies

Add to `requirements.txt`:
```
discord.py==2.3.2
python-telegram-bot==20.7
cryptography==41.0.7
django-encrypted-model-fields==0.6.5
```

## 🧪 Testing Requirements

### Unit Tests
- Model creation and validation
- Serializer validation
- Permission checks
- Token encryption/decryption

### Integration Tests
- Discord OAuth flow (mocked)
- Telegram bot connection (mocked)
- Channel syncing
- Token refresh logic

### API Tests
- All endpoint responses
- Error handling
- Permission enforcement
- Rate limiting

## 📝 Implementation Notes

1. **Security First**: All tokens must be encrypted at rest
2. **Rate Limiting**: Implement rate limiting for platform API calls
3. **Error Recovery**: Graceful handling of expired/revoked tokens
4. **Audit Trail**: Log all integration actions for security
5. **Background Tasks**: Use Celery for channel syncing
6. **Webhooks**: Consider Discord/Telegram webhooks for real-time updates

## 🚀 Future Enhancements

- Slack integration
- Microsoft Teams integration
- WhatsApp Business API integration
- Custom webhook integrations
- Integration health monitoring dashboard

# Made with Bob