# Integrations App Setup Guide

Complete guide to setting up the ChatSift Integrations app for Discord and Telegram.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Discord OAuth Setup](#discord-oauth-setup)
4. [Telegram Bot Setup](#telegram-bot-setup)
5. [Database Setup](#database-setup)
6. [Redis & Celery Setup](#redis--celery-setup)
7. [Testing the Setup](#testing-the-setup)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.10+
- Redis 6.0+
- PostgreSQL 13+ or SQLite (development)
- Virtual environment

### Python Packages
All required packages are in `requirements.txt`:
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
pip install -r requirements.txt
```

## Environment Setup

### 1. Copy Environment Template
```bash
cd backend
cp .env.example .env
```

### 2. Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Configure .env File

Edit `backend/.env` with your values:

```bash
# Django Settings
SECRET_KEY=your-django-secret-key-here
FIELD_ENCRYPTION_KEY=your-fernet-key-from-step-2
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# SendGrid (Optional - for production emails)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@chatsift.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Discord OAuth (see Discord OAuth Setup section)
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
DISCORD_REDIRECT_URI=http://localhost:8000/api/v1/integrations/discord/callback/
```

## Discord OAuth Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your application (e.g., "ChatSift")
4. Click "Create"

### 2. Configure OAuth2

1. Go to "OAuth2" → "General"
2. Copy your **Client ID** and **Client Secret**
3. Add to `.env`:
   ```bash
   DISCORD_CLIENT_ID=your_client_id_here
   DISCORD_CLIENT_SECRET=your_client_secret_here
   ```

### 3. Add Redirect URI

1. In "OAuth2" → "General" → "Redirects"
2. Add: `http://localhost:8000/api/v1/integrations/discord/callback/`
3. For production, add: `https://yourdomain.com/api/v1/integrations/discord/callback/`
4. Click "Save Changes"

### 4. Configure Bot (Optional)

If you want to use Discord bot features:
1. Go to "Bot" tab
2. Click "Add Bot"
3. Enable required intents:
   - Server Members Intent
   - Message Content Intent
4. Copy bot token (keep it secret!)

### 5. Required OAuth2 Scopes

The app requests these scopes:
- `identify` - Get user info
- `guilds` - List user's servers
- `guilds.members.read` - Read server member info

### 6. Test OAuth Flow

```bash
# Start Django server
python manage.py runserver

# Visit in browser:
http://localhost:8000/api/v1/integrations/discord/authorize/

# You should be redirected to Discord for authorization
```

## Telegram Bot Setup

### 1. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the **bot token** (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Configure Bot

Send these commands to @BotFather:

```
/setdescription - Set bot description
/setabouttext - Set about text
/setuserpic - Upload bot profile picture
```

### 3. Get Bot Token

Users will provide their own bot tokens when connecting Telegram.
No global configuration needed in `.env`.

### 4. Test Bot

```python
# Test bot token validity
import requests

BOT_TOKEN = "your_bot_token_here"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
response = requests.get(url)
print(response.json())
```

## Database Setup

### 1. Run Migrations

```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Verify Tables

```bash
python manage.py dbshell
```

```sql
-- Check integrations tables
.tables
SELECT * FROM platform_connections LIMIT 5;
SELECT * FROM channels LIMIT 5;
.quit
```

## Redis & Celery Setup

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### 2. Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### 3. Start Celery Worker

In a new terminal:
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
celery -A Infobyte worker --loglevel=info
```

### 4. Start Celery Beat (Optional)

For scheduled tasks, in another terminal:
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
celery -A Infobyte beat --loglevel=info
```

## Testing the Setup

### 1. Run Django Server

```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
python manage.py runserver
```

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/integrations/

# Discord OAuth URL
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/integrations/discord/authorize/
```

### 3. Run Tests

```bash
# Run all integration tests
python manage.py test integrations

# Run specific test file
python manage.py test integrations.tests.test_api

# Run with coverage
pip install coverage
coverage run --source='integrations' manage.py test integrations
coverage report
```

### 4. Test Celery Tasks

```bash
# Manual sync
python manage.py sync_integrations --all

# Async sync (requires Celery worker)
python manage.py sync_integrations --all --async
```

## Troubleshooting

### Discord OAuth Issues

**Problem:** "Invalid redirect_uri"
- **Solution:** Ensure redirect URI in Discord app matches exactly (including trailing slash)

**Problem:** "Invalid client_id"
- **Solution:** Verify DISCORD_CLIENT_ID in .env matches Discord app

**Problem:** "Access denied"
- **Solution:** User needs to authorize the requested scopes

### Telegram Bot Issues

**Problem:** "Unauthorized" error
- **Solution:** Verify bot token format and validity with @BotFather

**Problem:** "Bot not found"
- **Solution:** Ensure bot is not deleted and token is correct

**Problem:** "Can't access chat"
- **Solution:** Bot must be added to the group/channel first

### Database Issues

**Problem:** "no such table: platform_connections"
- **Solution:** Run migrations: `python manage.py migrate`

**Problem:** "UNIQUE constraint failed"
- **Solution:** Connection already exists for this user/platform

### Celery Issues

**Problem:** "Connection refused" to Redis
- **Solution:** Start Redis: `redis-server` or `brew services start redis`

**Problem:** Tasks not executing
- **Solution:** Ensure Celery worker is running

**Problem:** "Task timeout"
- **Solution:** Increase CELERY_TASK_TIME_LIMIT in settings

### Encryption Issues

**Problem:** "FIELD_ENCRYPTION_KEY must be defined"
- **Solution:** Generate and add Fernet key to .env

**Problem:** "Fernet key must be 32 url-safe base64-encoded bytes"
- **Solution:** Use proper key generation: `Fernet.generate_key()`

## Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Generate new FIELD_ENCRYPTION_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use HTTPS for all URLs
- [ ] Enable Redis authentication
- [ ] Use environment variables (never commit .env)
- [ ] Set up proper CORS origins
- [ ] Configure SendGrid for production emails
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure backup strategy

## Next Steps

1. **Configure Frontend**: Set up frontend to use these API endpoints
2. **Test Integration**: Create test connections for Discord and Telegram
3. **Monitor Tasks**: Use Celery Flower for task monitoring
4. **Set Up Logging**: Configure proper logging for production
5. **Deploy**: Follow deployment guide for production setup

## Support

For issues or questions:
- Check [CELERY_SETUP.md](../CELERY_SETUP.md) for Celery-specific help
- Review [ACCOUNTS_API_DOCUMENTATION.md](../../accounts/docs/ACCOUNTS_API_DOCUMENTATION.md) for auth
- Check Django logs: `tail -f logs/django.log`
- Check Celery logs: `tail -f logs/celery.log`

## Made with Bob