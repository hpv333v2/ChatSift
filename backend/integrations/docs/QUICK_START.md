# Integrations Quick Start Guide

Get up and running with ChatSift Integrations in 10 minutes.

## Prerequisites

- Python 3.10+
- Redis installed and running
- Virtual environment activated
- Django project set up

## Step 1: Install Dependencies (2 minutes)

```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
pip install -r requirements.txt
```

## Step 2: Configure Environment (3 minutes)

### Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Create .env File

```bash
cp .env.example .env
```

### Edit .env

Add the generated key and basic configuration:

```bash
# Required
SECRET_KEY=your-django-secret-key
FIELD_ENCRYPTION_KEY=your-generated-fernet-key-here
DEBUG=True

# Optional for now (can configure later)
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=http://localhost:8000/api/v1/integrations/discord/callback/
```

## Step 3: Run Migrations (1 minute)

```bash
python manage.py migrate
```

## Step 4: Create Superuser (1 minute)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## Step 5: Start Services (2 minutes)

### Terminal 1: Django Server

```bash
python manage.py runserver
```

### Terminal 2: Celery Worker (Optional)

```bash
celery -A Infobyte worker --loglevel=info
```

### Terminal 3: Celery Beat (Optional)

```bash
celery -A Infobyte beat --loglevel=info
```

## Step 6: Verify Setup (1 minute)

```bash
python manage.py validate_setup
```

This will check all configurations and report any issues.

## Quick Test

### 1. Get JWT Token

```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

Save the `access` token from the response.

### 2. List Integrations

```bash
export TOKEN="your_access_token_here"

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/
```

You should see an empty list of connections.

### 3. Test Discord OAuth (Optional)

If you configured Discord OAuth:

```bash
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/discord/authorize/
```

You'll get an authorization URL to visit in your browser.

## Next Steps

### Configure Discord OAuth

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Get Client ID and Client Secret
4. Add redirect URI: `http://localhost:8000/api/v1/integrations/discord/callback/`
5. Update `.env` with credentials

### Configure Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token
4. Use it when connecting via API

### Test Integration Flow

#### Discord:

```bash
# 1. Get authorization URL
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/discord/authorize/

# 2. Visit the URL in browser and authorize
# 3. You'll be redirected back with a connection created

# 4. List connections
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/
```

#### Telegram:

```bash
# Connect bot
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bot_token":"YOUR_BOT_TOKEN"}' \
  http://localhost:8000/api/v1/integrations/telegram/connect/

# List connections
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/
```

## Common Issues

### "FIELD_ENCRYPTION_KEY must be defined"

**Solution:** Generate and add encryption key to `.env`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### "Connection refused" to Redis

**Solution:** Start Redis:
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### "no such table: platform_connections"

**Solution:** Run migrations:
```bash
python manage.py migrate
```

### "Email verification required"

**Solution:** Verify email first:
```bash
# Get verification status
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/auth/email/status/

# Send verification email
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/email/verify/send/
```

For development, you can manually verify in Django admin or database.

## Development Workflow

### 1. Make Changes

Edit code in `backend/integrations/`

### 2. Run Tests

```bash
python manage.py test integrations
```

### 3. Check Coverage

```bash
pip install coverage
coverage run --source='integrations' manage.py test integrations
coverage report
coverage html  # Open htmlcov/index.html
```

### 4. Manual Testing

```bash
# Sync connections manually
python manage.py sync_integrations --all

# Check connection health
python manage.py sync_integrations --health-check

# Validate setup
python manage.py validate_setup
```

## Production Deployment

See [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md) for complete deployment guide.

Quick checklist:
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper Redis instance
- [ ] Configure Discord OAuth with production URLs
- [ ] Set up Celery workers with Supervisor/systemd
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging

## Useful Commands

```bash
# Validate setup
python manage.py validate_setup

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test integrations

# Sync integrations
python manage.py sync_integrations --all

# Start Celery worker
celery -A Infobyte worker --loglevel=info

# Start Celery beat
celery -A Infobyte beat --loglevel=info

# Monitor Celery with Flower
pip install flower
celery -A Infobyte flower
# Visit http://localhost:5555
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/integrations/` | GET | List all connections |
| `/integrations/{id}/` | GET | Get connection details |
| `/integrations/{id}/` | DELETE | Delete connection |
| `/integrations/{id}/refresh/` | POST | Refresh channels |
| `/integrations/discord/authorize/` | GET | Get Discord OAuth URL |
| `/integrations/discord/callback/` | GET | Discord OAuth callback |
| `/integrations/telegram/connect/` | POST | Connect Telegram bot |

## Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [Celery Setup](../CELERY_SETUP.md) - Background tasks guide
- [Deployment Checklist](../DEPLOYMENT_CHECKLIST.md) - Production deployment

## Support

- Check logs: `tail -f logs/django.log`
- Check Celery logs: `tail -f logs/celery.log`
- Run validation: `python manage.py validate_setup`
- Check Redis: `redis-cli ping`

## Made with Bob