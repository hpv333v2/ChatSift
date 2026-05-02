# Celery Setup Guide for Integrations

This guide explains how to set up and run Celery for background task processing in the integrations app.

## Prerequisites

1. **Redis** - Required as the message broker and result backend
2. **Python packages** - Install from requirements.txt

## Installation

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 2. Install Python Dependencies

```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Add to your `.env` file:
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running Celery

### Development Setup

You need to run **three separate processes**:

#### 1. Django Development Server
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
python manage.py runserver
```

#### 2. Celery Worker (in a new terminal)
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
celery -A Infobyte worker --loglevel=info
```

#### 3. Celery Beat (in a new terminal) - For scheduled tasks
```bash
source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate
cd backend
celery -A Infobyte beat --loglevel=info
```

### Production Setup

For production, use a process manager like **Supervisor** or **systemd**.

#### Example Supervisor Configuration

Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A Infobyte worker --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600

[program:celery-beat]
command=/path/to/venv/bin/celery -A Infobyte beat --loglevel=info
directory=/path/to/backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.log
autostart=true
autorestart=true
startsecs=10
```

## Available Tasks

### Periodic Tasks (Celery Beat)

These run automatically on a schedule:

1. **sync_all_connections** - Runs every hour
   - Syncs channels for all active connections

2. **refresh_expired_discord_tokens** - Runs daily at 2 AM
   - Refreshes Discord OAuth tokens expiring within 24 hours

3. **check_connection_health** - Runs every 6 hours
   - Verifies all connections are still valid

4. **cleanup_failed_connections** - Runs weekly on Sunday at 3 AM
   - Removes connections in error state for >30 days

### Manual Tasks

You can trigger tasks manually using the management command:

```bash
# Sync a specific connection
python manage.py sync_integrations --connection <connection_id>

# Sync all connections for a user
python manage.py sync_integrations --user <user_id>

# Sync all active connections
python manage.py sync_integrations --all

# Run health check
python manage.py sync_integrations --health-check

# Refresh expiring tokens
python manage.py sync_integrations --refresh-tokens

# Run asynchronously (requires Celery worker)
python manage.py sync_integrations --all --async
```

## Monitoring

### Celery Flower (Web-based monitoring)

Install Flower:
```bash
pip install flower
```

Run Flower:
```bash
celery -A Infobyte flower
```

Access at: http://localhost:5555

### Check Task Status

```python
from integrations.tasks import sync_connection_channels

# Queue a task
result = sync_connection_channels.delay('connection-id')

# Check status
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocks until complete)
print(result.get(timeout=10))
```

## Troubleshooting

### Redis Connection Issues

Check if Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Worker Not Processing Tasks

1. Check worker logs for errors
2. Verify Redis connection
3. Ensure tasks are properly registered:
   ```bash
   celery -A Infobyte inspect registered
   ```

### Tasks Failing

1. Check worker logs: `celery -A Infobyte worker --loglevel=debug`
2. Verify environment variables are set
3. Check database connections
4. Verify API credentials (Discord/Telegram)

## Task Retry Logic

Tasks automatically retry on failure:
- **sync_connection_channels**: 3 retries, 5-minute delay
- **refresh_discord_token**: 3 retries, 10-minute delay
- **sync_user_connections**: 2 retries, 3-minute delay

## Performance Tuning

### Worker Concurrency

Adjust based on your server:
```bash
# 4 worker processes
celery -A Infobyte worker --concurrency=4

# Auto-scale between 2-8 workers
celery -A Infobyte worker --autoscale=8,2
```

### Task Time Limits

Configured in `Infobyte/celery.py`:
- Hard limit: 30 minutes
- Soft limit: 25 minutes

### Prefetch Multiplier

Set to 1 for long-running tasks to prevent worker blocking.

## Security Notes

1. **Never commit** `.env` file with real credentials
2. Use **separate Redis databases** for different environments
3. Enable **Redis authentication** in production
4. Use **SSL/TLS** for Redis connections in production

## Made with Bob