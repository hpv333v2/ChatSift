# ChatSift Backend Architecture Plan

## 🎯 Project Overview
ChatSift is an AI-powered application that transforms high-volume group chats into concise, actionable daily summaries by integrating with Discord and Telegram platforms.

## 📁 Directory Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── Infobyte/                    # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev-specific settings
│   │   └── production.py       # Prod-specific settings
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py                 # Root URL configuration
│   └── celery.py               # Celery configuration
│
├── apps/
│   ├── accounts/               # User management & authentication
│   │   ├── __init__.py
│   │   ├── models.py           # User, UserProfile
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   └── tests/
│   │
│   ├── integrations/           # Platform integrations
│   │   ├── __init__.py
│   │   ├── models.py           # PlatformConnection, Channel
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── discord_service.py
│   │   │   ├── telegram_service.py
│   │   │   └── base_service.py
│   │   └── tests/
│   │
│   ├── messages/               # Message storage & retrieval
│   │   ├── __init__.py
│   │   ├── models.py           # Message, MessageBatch
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py
│   │   └── tests/
│   │
│   ├── summaries/              # AI summarization
│   │   ├── __init__.py
│   │   ├── models.py           # Summary, SummarySection
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py
│   │   │   ├── summarizer.py
│   │   │   └── prompt_templates.py
│   │   └── tests/
│   │
│   ├── monitoring/             # Channel monitoring configuration
│   │   ├── __init__.py
│   │   ├── models.py           # MonitoredChannel, MonitoringSchedule
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── notifications/          # Delivery of summaries
│       ├── __init__.py
│       ├── models.py           # NotificationPreference, DeliveryLog
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── email_service.py
│       │   └── webhook_service.py
│       └── tests/
│
├── core/                       # Shared utilities
│   ├── __init__.py
│   ├── exceptions.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── utils.py
│   └── validators.py
│
├── tasks/                      # Celery tasks
│   ├── __init__.py
│   ├── message_fetcher.py      # Fetch messages from platforms
│   ├── summarizer.py           # Generate summaries
│   ├── scheduler.py            # Schedule periodic tasks
│   └── cleanup.py              # Data cleanup tasks
│
└── tests/                      # Integration tests
    ├── __init__.py
    ├── test_integration.py
    └── fixtures/
```

## 🗄️ Database Models

### 1. **accounts** App

#### User (extends Django's AbstractUser)
```python
- id: UUID (PK)
- email: EmailField (unique)
- username: CharField (unique)
- is_active: BooleanField
- date_joined: DateTimeField
- last_login: DateTimeField
```

#### UserProfile
```python
- id: UUID (PK)
- user: OneToOneField(User)
- timezone: CharField (default: UTC)
- preferred_summary_time: TimeField (e.g., 09:00)
- created_at: DateTimeField
- updated_at: DateTimeField
```

### 2. **integrations** App

#### PlatformConnection
```python
- id: UUID (PK)
- user: ForeignKey(User)
- platform: CharField (choices: DISCORD, TELEGRAM)
- platform_user_id: CharField (platform-specific user ID)
- access_token: EncryptedTextField
- refresh_token: EncryptedTextField (nullable)
- token_expires_at: DateTimeField (nullable)
- is_active: BooleanField
- connected_at: DateTimeField
- last_synced_at: DateTimeField (nullable)
- metadata: JSONField (platform-specific data)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- (user, platform) - unique together
- platform_user_id
```

#### Channel
```python
- id: UUID (PK)
- connection: ForeignKey(PlatformConnection)
- platform_channel_id: CharField (platform-specific channel ID)
- channel_name: CharField
- channel_type: CharField (choices: TEXT, VOICE, GROUP, PRIVATE)
- is_accessible: BooleanField
- member_count: IntegerField (nullable)
- metadata: JSONField (channel-specific data)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- (connection, platform_channel_id) - unique together
- channel_name
```

### 3. **monitoring** App

#### MonitoredChannel
```python
- id: UUID (PK)
- user: ForeignKey(User)
- channel: ForeignKey(Channel)
- is_active: BooleanField
- monitoring_start_date: DateField
- monitoring_end_date: DateField (nullable)
- fetch_frequency: CharField (choices: HOURLY, EVERY_6_HOURS, DAILY)
- last_fetched_at: DateTimeField (nullable)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- (user, channel) - unique together
- is_active
- last_fetched_at
```

#### MonitoringSchedule
```python
- id: UUID (PK)
- monitored_channel: ForeignKey(MonitoredChannel)
- schedule_type: CharField (choices: FETCH, SUMMARIZE)
- cron_expression: CharField
- is_active: BooleanField
- last_run_at: DateTimeField (nullable)
- next_run_at: DateTimeField
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- next_run_at
- is_active
```

### 4. **messages** App

#### MessageBatch
```python
- id: UUID (PK)
- monitored_channel: ForeignKey(MonitoredChannel)
- batch_start_time: DateTimeField
- batch_end_time: DateTimeField
- message_count: IntegerField
- fetch_status: CharField (choices: PENDING, IN_PROGRESS, COMPLETED, FAILED)
- error_message: TextField (nullable)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- monitored_channel
- batch_start_time
- fetch_status
```

#### Message
```python
- id: UUID (PK)
- batch: ForeignKey(MessageBatch)
- platform_message_id: CharField (platform-specific message ID)
- author_id: CharField (platform user ID)
- author_name: CharField
- content: TextField
- message_type: CharField (choices: TEXT, IMAGE, FILE, LINK, SYSTEM)
- timestamp: DateTimeField (message creation time on platform)
- has_attachments: BooleanField
- attachments: JSONField (nullable)
- reactions: JSONField (nullable)
- is_reply: BooleanField
- reply_to_message_id: CharField (nullable)
- metadata: JSONField (platform-specific data)
- created_at: DateTimeField

Indexes:
- batch
- platform_message_id
- timestamp
- author_id
```

### 5. **summaries** App

#### Summary
```python
- id: UUID (PK)
- monitored_channel: ForeignKey(MonitoredChannel)
- batch: ForeignKey(MessageBatch)
- summary_date: DateField
- summary_period_start: DateTimeField
- summary_period_end: DateTimeField
- total_messages: IntegerField
- active_participants: IntegerField
- generation_status: CharField (choices: PENDING, GENERATING, COMPLETED, FAILED)
- llm_model: CharField (e.g., gpt-4, claude-3)
- llm_tokens_used: IntegerField (nullable)
- error_message: TextField (nullable)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- monitored_channel
- summary_date
- generation_status
```

#### SummarySection
```python
- id: UUID (PK)
- summary: ForeignKey(Summary)
- section_type: CharField (choices: KEY_POINTS, DECISIONS, ACTION_ITEMS, TRENDS, HIGHLIGHTS)
- section_order: IntegerField
- title: CharField
- content: TextField
- confidence_score: FloatField (0.0-1.0, nullable)
- created_at: DateTimeField

Indexes:
- (summary, section_order)
```

### 6. **notifications** App

#### NotificationPreference
```python
- id: UUID (PK)
- user: OneToOneField(User)
- email_enabled: BooleanField
- email_address: EmailField (nullable)
- webhook_enabled: BooleanField
- webhook_url: URLField (nullable)
- delivery_time: TimeField (preferred delivery time)
- delivery_timezone: CharField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### DeliveryLog
```python
- id: UUID (PK)
- summary: ForeignKey(Summary)
- user: ForeignKey(User)
- delivery_method: CharField (choices: EMAIL, WEBHOOK, IN_APP)
- delivery_status: CharField (choices: PENDING, SENT, FAILED, RETRYING)
- delivered_at: DateTimeField (nullable)
- error_message: TextField (nullable)
- retry_count: IntegerField (default: 0)
- created_at: DateTimeField
- updated_at: DateTimeField

Indexes:
- summary
- user
- delivery_status
- delivered_at
```

## 🔌 REST API Endpoints

### Authentication & User Management

```
POST   /api/v1/auth/register/              # User registration
POST   /api/v1/auth/login/                 # User login (JWT)
POST   /api/v1/auth/logout/                # User logout
POST   /api/v1/auth/refresh/               # Refresh JWT token
POST   /api/v1/auth/password/reset/        # Request password reset
POST   /api/v1/auth/password/reset/confirm/ # Confirm password reset

GET    /api/v1/users/me/                   # Get current user profile
PATCH  /api/v1/users/me/                   # Update user profile
DELETE /api/v1/users/me/                   # Delete user account
```

### Platform Integrations

```
# Discord Integration
GET    /api/v1/integrations/discord/authorize/     # Get Discord OAuth URL
POST   /api/v1/integrations/discord/callback/      # Handle OAuth callback
GET    /api/v1/integrations/discord/connections/   # List Discord connections
DELETE /api/v1/integrations/discord/connections/{id}/ # Disconnect Discord

# Telegram Integration
POST   /api/v1/integrations/telegram/connect/      # Connect via bot token
GET    /api/v1/integrations/telegram/connections/  # List Telegram connections
DELETE /api/v1/integrations/telegram/connections/{id}/ # Disconnect Telegram

# Generic Connection Management
GET    /api/v1/integrations/connections/           # List all connections
GET    /api/v1/integrations/connections/{id}/      # Get connection details
PATCH  /api/v1/integrations/connections/{id}/      # Update connection
POST   /api/v1/integrations/connections/{id}/sync/ # Trigger manual sync
```

### Channel Management

```
GET    /api/v1/channels/                           # List available channels
GET    /api/v1/channels/{id}/                      # Get channel details
POST   /api/v1/channels/sync/                      # Sync channels from platforms
GET    /api/v1/channels/search/?q={query}          # Search channels
```

### Monitoring Configuration

```
GET    /api/v1/monitoring/channels/                # List monitored channels
POST   /api/v1/monitoring/channels/                # Add channel to monitoring
GET    /api/v1/monitoring/channels/{id}/           # Get monitoring details
PATCH  /api/v1/monitoring/channels/{id}/           # Update monitoring config
DELETE /api/v1/monitoring/channels/{id}/           # Stop monitoring channel
POST   /api/v1/monitoring/channels/{id}/pause/     # Pause monitoring
POST   /api/v1/monitoring/channels/{id}/resume/    # Resume monitoring

GET    /api/v1/monitoring/schedules/               # List monitoring schedules
POST   /api/v1/monitoring/schedules/               # Create custom schedule
PATCH  /api/v1/monitoring/schedules/{id}/          # Update schedule
DELETE /api/v1/monitoring/schedules/{id}/          # Delete schedule
```

### Messages

```
GET    /api/v1/messages/                           # List messages (paginated)
GET    /api/v1/messages/{id}/                      # Get message details
GET    /api/v1/messages/batches/                   # List message batches
GET    /api/v1/messages/batches/{id}/              # Get batch details
GET    /api/v1/messages/batches/{id}/messages/     # Get messages in batch
POST   /api/v1/messages/fetch/                     # Trigger manual fetch
```

### Summaries

```
GET    /api/v1/summaries/                          # List summaries (paginated)
POST   /api/v1/summaries/                          # Generate summary manually
GET    /api/v1/summaries/{id}/                     # Get summary details
GET    /api/v1/summaries/{id}/sections/            # Get summary sections
POST   /api/v1/summaries/{id}/regenerate/          # Regenerate summary
DELETE /api/v1/summaries/{id}/                     # Delete summary
GET    /api/v1/summaries/latest/                   # Get latest summaries
GET    /api/v1/summaries/stats/                    # Get summary statistics
```

### Notifications

```
GET    /api/v1/notifications/preferences/          # Get notification preferences
PATCH  /api/v1/notifications/preferences/          # Update preferences
GET    /api/v1/notifications/delivery-logs/        # List delivery logs
GET    /api/v1/notifications/delivery-logs/{id}/   # Get delivery log details
POST   /api/v1/notifications/test/                 # Send test notification
```

### Dashboard & Analytics

```
GET    /api/v1/dashboard/overview/                 # Dashboard overview stats
GET    /api/v1/dashboard/activity/                 # Recent activity feed
GET    /api/v1/analytics/message-trends/           # Message volume trends
GET    /api/v1/analytics/channel-stats/            # Per-channel statistics
GET    /api/v1/analytics/summary-metrics/          # Summary generation metrics
```

## 🔗 Platform Integration Architecture

### Discord Integration

**Authentication Flow:**
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Discord

    User->>Frontend: Click "Connect Discord"
    Frontend->>Backend: GET /api/v1/integrations/discord/authorize/
    Backend->>Frontend: Return OAuth URL
    Frontend->>Discord: Redirect to OAuth URL
    Discord->>User: Request permissions
    User->>Discord: Grant permissions
    Discord->>Backend: Redirect with code
    Backend->>Discord: Exchange code for token
    Discord->>Backend: Return access token
    Backend->>Backend: Store encrypted token
    Backend->>Frontend: Redirect to success page
```

**Implementation Details:**
- Use `discord.py` library for Discord API interaction
- OAuth2 flow for user authentication
- Bot token for server/channel access
- Webhook support for real-time message events
- Rate limiting: 50 requests per second per bot

**Key Services:**
- `DiscordAuthService`: Handle OAuth flow
- `DiscordChannelService`: Fetch channels and guilds
- `DiscordMessageService`: Fetch messages with pagination
- `DiscordWebhookService`: Handle real-time events

### Telegram Integration

**Authentication Flow:**
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant TelegramBot
    participant Telegram

    User->>Frontend: Click "Connect Telegram"
    Frontend->>Backend: POST /api/v1/integrations/telegram/connect/
    Backend->>User: Return bot username
    User->>TelegramBot: Send /start command
    TelegramBot->>Backend: Webhook with user info
    Backend->>Backend: Link user account
    Backend->>TelegramBot: Send confirmation
    TelegramBot->>User: "Connected successfully"
```

**Implementation Details:**
- Use `python-telegram-bot` library
- Bot-based authentication (no OAuth)
- Long polling or webhook for message updates
- Support for groups and channels
- Rate limiting: 30 messages per second

**Key Services:**
- `TelegramBotService`: Bot initialization and commands
- `TelegramChannelService`: Fetch chats and channels
- `TelegramMessageService`: Fetch messages with pagination
- `TelegramWebhookService`: Handle webhook updates

## 🤖 AI/LLM Summarization Service

### Architecture

```mermaid
graph TD
    A[Message Batch] --> B[Preprocessor]
    B --> C[Context Builder]
    C --> D[LLM Service]
    D --> E[Response Parser]
    E --> F[Summary Sections]
    
    B --> G[Filter Noise]
    B --> H[Deduplicate]
    B --> I[Extract Metadata]
    
    D --> J[OpenAI GPT-4]
    D --> K[Anthropic Claude]
    D --> L[Local LLM]
```

### LLM Service Components

**1. Preprocessor**
- Remove bot messages and system notifications
- Filter spam and irrelevant content
- Deduplicate similar messages
- Extract URLs, mentions, and hashtags
- Identify conversation threads

**2. Context Builder**
- Group messages by topic/thread
- Identify key participants
- Extract temporal patterns
- Build conversation context
- Prepare prompt with structured data

**3. LLM Integration**
- Support multiple LLM providers (OpenAI, Anthropic, local models)
- Configurable model selection per user
- Token usage tracking
- Retry logic with exponential backoff
- Fallback to alternative models

**4. Prompt Templates**
```python
SUMMARY_PROMPT = """
You are an AI assistant that summarizes group chat conversations.

Context:
- Channel: {channel_name}
- Date: {date}
- Messages: {message_count}
- Participants: {participant_count}

Messages:
{messages}

Generate a structured summary with:
1. Key Points (3-5 main topics discussed)
2. Decisions Made (if any)
3. Action Items (tasks or follow-ups mentioned)
4. Notable Trends (patterns or recurring themes)
5. Highlights (interesting or important moments)

Format as JSON with sections.
"""
```

**5. Response Parser**
- Parse LLM JSON response
- Validate structure
- Extract confidence scores
- Create SummarySection objects
- Handle parsing errors

### LLM Provider Configuration

```python
LLM_PROVIDERS = {
    'openai': {
        'model': 'gpt-4-turbo-preview',
        'max_tokens': 4000,
        'temperature': 0.3,
        'api_key': env('OPENAI_API_KEY')
    },
    'anthropic': {
        'model': 'claude-3-opus-20240229',
        'max_tokens': 4000,
        'temperature': 0.3,
        'api_key': env('ANTHROPIC_API_KEY')
    },
    'local': {
        'model': 'llama-2-70b',
        'endpoint': env('LOCAL_LLM_ENDPOINT'),
        'max_tokens': 4000
    }
}
```

## ⏰ Task Scheduling System (Celery)

### Celery Configuration

```python
# Infobyte/celery.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
```

### Scheduled Tasks

**1. Message Fetching Tasks**
```python
@shared_task
def fetch_messages_for_channel(monitored_channel_id):
    """
    Fetch new messages from a monitored channel
    Runs based on MonitoringSchedule configuration
    """
    pass

@shared_task
def fetch_all_due_channels():
    """
    Find all channels due for fetching and queue fetch tasks
    Runs every 5 minutes
    """
    pass
```

**2. Summary Generation Tasks**
```python
@shared_task
def generate_summary_for_batch(batch_id):
    """
    Generate AI summary for a message batch
    Triggered after message fetch completes
    """
    pass

@shared_task
def generate_daily_summaries():
    """
    Generate daily summaries for all active monitored channels
    Runs once per day at configured time
    """
    pass
```

**3. Notification Tasks**
```python
@shared_task
def send_summary_notification(summary_id, user_id):
    """
    Send summary to user via configured delivery method
    """
    pass

@shared_task
def send_daily_digest():
    """
    Send daily digest to all users at their preferred time
    Runs hourly, checks user timezones
    """
    pass
```

**4. Maintenance Tasks**
```python
@shared_task
def cleanup_old_messages():
    """
    Archive or delete messages older than retention period
    Runs daily at 2 AM
    """
    pass

@shared_task
def refresh_expired_tokens():
    """
    Refresh OAuth tokens that are about to expire
    Runs every hour
    """
    pass

@shared_task
def sync_channel_metadata():
    """
    Update channel names, member counts, etc.
    Runs daily at 3 AM
    """
    pass
```

### Celery Beat Schedule

```python
CELERY_BEAT_SCHEDULE = {
    'fetch-due-channels': {
        'task': 'tasks.message_fetcher.fetch_all_due_channels',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'generate-daily-summaries': {
        'task': 'tasks.summarizer.generate_daily_summaries',
        'schedule': crontab(hour=1, minute=0),  # 1 AM UTC
    },
    'send-daily-digest': {
        'task': 'tasks.scheduler.send_daily_digest',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-old-messages': {
        'task': 'tasks.cleanup.cleanup_old_messages',
        'schedule': crontab(hour=2, minute=0),  # 2 AM UTC
    },
    'refresh-tokens': {
        'task': 'tasks.scheduler.refresh_expired_tokens',
        'schedule': crontab(minute=0),  # Every hour
    },
    'sync-metadata': {
        'task': 'tasks.scheduler.sync_channel_metadata',
        'schedule': crontab(hour=3, minute=0),  # 3 AM UTC
    },
}
```

## 🔐 Authentication & Authorization

### Authentication Strategy

**JWT-based Authentication:**
- Access token (15 minutes expiry)
- Refresh token (7 days expiry)
- Token stored in httpOnly cookies
- CSRF protection enabled

**Implementation:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Authorization Rules

**Resource-Level Permissions:**
- Users can only access their own data
- Platform connections belong to specific users
- Monitored channels are user-specific
- Summaries are private to the user who created them

**Custom Permissions:**
```python
class IsOwner(permissions.BasePermission):
    """User can only access their own resources"""
    
class HasActiveConnection(permissions.BasePermission):
    """User must have active platform connection"""
    
class CanMonitorChannel(permissions.BasePermission):
    """User must have access to the channel"""
```

## 🔄 User Flow (Backend Perspective)

### 1. User Registration & Onboarding

```mermaid
graph TD
    A[User Registers] --> B[Create User Account]
    B --> C[Create UserProfile]
    C --> D[Set Default Preferences]
    D --> E[Send Welcome Email]
    E --> F[Return JWT Tokens]
```

### 2. Platform Connection Flow

```mermaid
graph TD
    A[User Initiates Connection] --> B{Platform Type?}
    B -->|Discord| C[OAuth Flow]
    B -->|Telegram| D[Bot Connection]
    C --> E[Store Encrypted Tokens]
    D --> E
    E --> F[Fetch Available Channels]
    F --> G[Return Channel List]
```

### 3. Channel Monitoring Setup

```mermaid
graph TD
    A[User Selects Channel] --> B[Create MonitoredChannel]
    B --> C[Create MonitoringSchedule]
    C --> D[Queue Initial Fetch Task]
    D --> E[Fetch Historical Messages]
    E --> F[Store Messages in Batch]
    F --> G[Return Monitoring Status]
```

### 4. Message Fetching Cycle

```mermaid
graph TD
    A[Celery Beat Triggers] --> B[Check Due Channels]
    B --> C[Queue Fetch Tasks]
    C --> D[Fetch from Platform API]
    D --> E[Create MessageBatch]
    E --> F[Store Messages]
    F --> G[Update last_fetched_at]
    G --> H{Enough Messages?}
    H -->|Yes| I[Queue Summary Task]
    H -->|No| J[Wait for Next Cycle]
```

### 5. Summary Generation Flow

```mermaid
graph TD
    A[Summary Task Triggered] --> B[Load Message Batch]
    B --> C[Preprocess Messages]
    C --> D[Build Context]
    D --> E[Call LLM API]
    E --> F[Parse Response]
    F --> G[Create Summary]
    G --> H[Create SummarySections]
    H --> I[Queue Notification Task]
```

### 6. Notification Delivery Flow

```mermaid
graph TD
    A[Notification Task] --> B[Load User Preferences]
    B --> C{Delivery Method?}
    C -->|Email| D[Send Email]
    C -->|Webhook| E[POST to Webhook]
    C -->|In-App| F[Store Notification]
    D --> G[Create DeliveryLog]
    E --> G
    F --> G
    G --> H{Success?}
    H -->|No| I[Schedule Retry]
    H -->|Yes| J[Mark as Delivered]
```

## 📦 Required Dependencies

```txt
# Core Framework
Django==6.0.4
djangorestframework==3.17.1
django-cors-headers==4.6.0

# Authentication
djangorestframework-simplejwt==5.4.1
django-allauth==65.4.0

# Database
psycopg2-binary==2.9.10  # PostgreSQL adapter
dj-database-url==2.3.0

# Task Queue
celery==5.4.0
redis==5.2.1
django-celery-beat==2.7.0
django-celery-results==2.5.1

# Platform Integrations
discord.py==2.4.0
python-telegram-bot==21.10
aiohttp==3.11.11

# AI/LLM
openai==1.59.7
anthropic==0.42.0
tiktoken==0.8.0  # Token counting

# Security
cryptography==44.0.0  # Token encryption
python-decouple==3.8  # Environment variables
django-environ==0.11.2

# Utilities
python-dateutil==2.9.0
pytz==2024.2
requests==2.32.3

# Monitoring & Logging
sentry-sdk==2.19.2
django-debug-toolbar==4.4.6

# Testing
pytest==8.3.4
pytest-django==4.9.0
pytest-cov==6.0.0
factory-boy==3.3.1
faker==33.1.0

# Code Quality
black==24.10.0
flake8==7.1.1
isort==5.13.2
```

## 🌍 Environment Configuration

### .env.example
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatsift
# or for SQLite: sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# Discord Integration
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_REDIRECT_URI=http://localhost:8000/api/v1/integrations/discord/callback/

# Telegram Integration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/v1/integrations/telegram/webhook/

# LLM Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DEFAULT_LLM_PROVIDER=openai

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Monitoring
SENTRY_DSN=your-sentry-dsn

# Feature Flags
ENABLE_DISCORD=True
ENABLE_TELEGRAM=True
ENABLE_EMAIL_NOTIFICATIONS=True
ENABLE_WEBHOOK_NOTIFICATIONS=True

# Data Retention
MESSAGE_RETENTION_DAYS=90
SUMMARY_RETENTION_DAYS=365
```

## 🚀 Deployment Considerations

### Production Settings

**Database:**
- Use PostgreSQL instead of SQLite
- Enable connection pooling
- Set up read replicas for scaling

**Caching:**
- Redis for Celery broker and result backend
- Django cache framework for API responses
- Cache channel lists and user preferences

**Security:**
- Use environment variables for secrets
- Enable HTTPS only
- Set secure cookie flags
- Implement rate limiting
- Add CORS configuration
- Enable CSRF protection

**Monitoring:**
- Sentry for error tracking
- Celery Flower for task monitoring
- Django Debug Toolbar (dev only)
- Custom metrics for API usage

**Scaling:**
- Horizontal scaling with load balancer
- Separate Celery workers for different task types
- Message queue for high-volume channels
- CDN for static files

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "Infobyte.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: chatsift
      POSTGRES_USER: chatsift
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    
  web:
    build: .
    command: gunicorn Infobyte.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery:
    build: .
    command: celery -A Infobyte worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery-beat:
    build: .
    command: celery -A Infobyte beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

## 📊 API Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "field": "value"
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": ["Error message"]
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Paginated Response
```json
{
  "status": "success",
  "data": {
    "results": [],
    "count": 100,
    "next": "http://api.example.com/resource/?page=2",
    "previous": null
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 🔍 Key Implementation Notes

1. **Token Security**: All OAuth tokens must be encrypted at rest using Django's `cryptography` library
2. **Rate Limiting**: Implement per-user rate limits to prevent API abuse
3. **Idempotency**: Message fetching should be idempotent to handle retries
4. **Error Handling**: Graceful degradation when platform APIs are unavailable
5. **Data Privacy**: Users can only access their own data; strict permission checks
6. **Scalability**: Design for horizontal scaling from day one
7. **Testing**: Comprehensive test coverage for critical paths
8. **Documentation**: Auto-generate API docs using drf-spectacular
9. **Logging**: Structured logging for debugging and monitoring
10. **Migrations**: Use Django migrations for all schema changes

---

**Next Steps:**
1. Review and approve this architecture plan
2. Set up development environment
3. Create Django apps with models
4. Implement authentication system
5. Build platform integration services
6. Develop LLM summarization pipeline
7. Set up Celery task scheduling
8. Create REST API endpoints
9. Write comprehensive tests
10. Deploy to staging environment