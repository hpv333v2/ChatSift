# ChatSift Integrations App

Django app for managing Discord and Telegram integrations with automated channel syncing and background task processing.

## Features

✅ **Discord Integration**
- OAuth2 authentication flow
- Automatic server and channel discovery
- Token refresh management
- Real-time channel syncing

✅ **Telegram Integration**
- Bot token validation
- Group and channel discovery
- Webhook support (planned)
- Message polling

✅ **Background Tasks**
- Automated channel syncing (hourly)
- Token refresh (daily)
- Health checks (every 6 hours)
- Failed connection cleanup (weekly)

✅ **Security**
- Encrypted token storage (Fernet)
- Email verification requirement
- Permission-based access control
- CSRF protection for OAuth

✅ **API**
- RESTful endpoints
- JWT authentication
- Comprehensive error handling
- Rate limiting ready

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Run migrations
python manage.py migrate

# 4. Start server
python manage.py runserver

# 5. Start Celery (optional)
celery -A Infobyte worker --loglevel=info
```

See [QUICK_START.md](docs/QUICK_START.md) for detailed instructions.

## Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 10 minutes
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[Celery Setup](CELERY_SETUP.md)** - Background tasks configuration
- **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Production deployment guide

## Architecture

```
integrations/
├── models.py              # PlatformConnection, Channel models
├── serializers.py         # API serializers with validation
├── views.py              # API endpoints
├── permissions.py        # Custom permissions
├── tasks.py              # Celery background tasks
├── admin.py              # Django admin configuration
├── services/
│   ├── base_service.py   # Abstract base service
│   ├── discord_service.py # Discord API integration
│   └── telegram_service.py # Telegram Bot API integration
├── management/
│   └── commands/
│       ├── sync_integrations.py  # Manual sync command
│       └── validate_setup.py     # Setup validation
└── tests/
    ├── test_models.py
    ├── test_serializers.py
    ├── test_permissions.py
    ├── test_discord_service.py
    ├── test_telegram_service.py
    ├── test_views.py
    └── test_api.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/integrations/` | GET | List all connections |
| `/integrations/{id}/` | GET | Get connection details |
| `/integrations/{id}/` | DELETE | Delete connection |
| `/integrations/{id}/refresh/` | POST | Refresh channels |
| `/integrations/discord/authorize/` | GET | Get Discord OAuth URL |
| `/integrations/discord/callback/` | GET | Discord OAuth callback |
| `/integrations/telegram/connect/` | POST | Connect Telegram bot |

## Models

### PlatformConnection

Stores integration connections with encrypted tokens.

**Fields:**
- `user` - Foreign key to User
- `platform` - 'discord' or 'telegram'
- `platform_user_id` - Platform-specific user ID
- `platform_username` - Platform username
- `access_token` - Encrypted OAuth token (Discord)
- `refresh_token` - Encrypted refresh token (Discord)
- `bot_token` - Encrypted bot token (Telegram)
- `status` - 'active', 'error', or 'disconnected'
- `token_expires_at` - Token expiration timestamp
- `last_synced` - Last channel sync timestamp

### Channel

Stores discovered channels/servers.

**Fields:**
- `connection` - Foreign key to PlatformConnection
- `channel_id` - Platform-specific channel ID
- `channel_name` - Channel/server name
- `channel_type` - Type (guild, channel, group, etc.)
- `parent_channel_id` - Parent channel (for nested channels)
- `is_active` - Whether channel is still accessible
- `permissions` - JSON field with permissions
- `metadata` - JSON field with additional data

## Background Tasks

### Periodic Tasks (Celery Beat)

- **sync_all_connections** - Every hour
  - Syncs channels for all active connections
  
- **refresh_expired_discord_tokens** - Daily at 2 AM
  - Refreshes Discord tokens expiring within 24 hours
  
- **check_connection_health** - Every 6 hours
  - Verifies connections are still valid
  
- **cleanup_failed_connections** - Weekly (Sunday 3 AM)
  - Removes connections in error state for >30 days

### Manual Tasks

```bash
# Sync specific connection
python manage.py sync_integrations --connection <uuid>

# Sync all connections for a user
python manage.py sync_integrations --user <user_id>

# Sync all active connections
python manage.py sync_integrations --all

# Run health check
python manage.py sync_integrations --health-check

# Refresh expiring tokens
python manage.py sync_integrations --refresh-tokens
```

## Testing

```bash
# Run all tests
python manage.py test integrations

# Run specific test file
python manage.py test integrations.tests.test_api

# Run with coverage
coverage run --source='integrations' manage.py test integrations
coverage report
coverage html
```

**Test Coverage:** 86 tests covering:
- Models and database operations
- Serializers and validation
- Permissions and access control
- Discord service integration
- Telegram service integration
- API endpoints
- View logic

## Configuration

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
FIELD_ENCRYPTION_KEY=your-fernet-key
DEBUG=True

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Discord OAuth
DISCORD_CLIENT_ID=your-client-id
DISCORD_CLIENT_SECRET=your-client-secret
DISCORD_REDIRECT_URI=http://localhost:8000/api/v1/integrations/discord/callback/
```

### Optional Environment Variables

```bash
# Email (for production)
SENDGRID_API_KEY=your-sendgrid-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Frontend
FRONTEND_URL=http://localhost:3000

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Security

### Token Encryption

All sensitive tokens are encrypted using Fernet (symmetric encryption):
- Discord OAuth tokens
- Discord refresh tokens
- Telegram bot tokens

### Permissions

- **IsEmailVerified** - Email must be verified to create integrations
- **IsConnectionOwner** - Users can only access their own connections
- **CanManageConnection** - Users can only manage their own connections

### CSRF Protection

Discord OAuth flow uses state-based CSRF protection with session storage.

## Performance

### Database Indexes

- `(user, platform)` - Fast connection lookups
- `status` - Fast active connection queries
- `(connection, is_active)` - Fast channel queries
- `channel_type` - Fast channel type filtering

### Caching

- Connection status cached for 5 minutes
- Channel lists cached for 15 minutes
- Token expiration checked before API calls

### Rate Limiting

Recommended rate limits:
- Discord OAuth: 10 requests/minute per user
- Telegram Connect: 5 requests/minute per user
- Connection Management: 60 requests/minute per user
- Refresh: 10 requests/minute per connection

## Monitoring

### Health Checks

```bash
# Validate setup
python manage.py validate_setup

# Check Celery workers
celery -A Infobyte inspect active

# Check scheduled tasks
celery -A Infobyte inspect scheduled
```

### Logging

Logs are written to:
- Django logs: `logs/django.log`
- Celery logs: `logs/celery.log`

Log levels:
- INFO: Normal operations
- WARNING: Recoverable errors
- ERROR: Failed operations
- CRITICAL: System failures

### Metrics

Track these metrics:
- Active connections count
- Failed connections count
- Channel sync success rate
- Token refresh success rate
- API response times
- Celery task execution times

## Troubleshooting

### Common Issues

**"FIELD_ENCRYPTION_KEY must be defined"**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**"Connection refused" to Redis**
```bash
redis-cli ping  # Should return PONG
```

**"no such table: platform_connections"**
```bash
python manage.py migrate
```

**Discord OAuth fails**
- Check redirect URI matches exactly
- Verify client ID and secret
- Check Discord app is not deleted

**Telegram bot fails**
- Verify bot token format
- Check bot is not deleted
- Ensure bot is added to groups

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for more troubleshooting.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests: `python manage.py test integrations`
6. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions:
- Check documentation in `docs/`
- Review test files for examples
- Check Django logs for errors
- Run `python manage.py validate_setup`

## Made with Bob

Built with ❤️ using Django, Celery, and Redis.