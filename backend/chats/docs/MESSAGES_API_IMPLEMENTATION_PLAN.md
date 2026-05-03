# 📨 Messages API - Implementation Plan

## 📋 Overview
The messages app handles fetching, storing, and managing chat messages from monitored channels. It serves as the data layer between platform integrations and summary generation.

## 🎯 Purpose
- Fetch messages from Discord/Telegram via integration services
- Store messages in batches with metadata
- Provide API for message retrieval and search
- Track fetch status and handle failures

## 📊 Dependencies
- **Upstream:** [`monitoring`](../monitoring/) (MonitoredChannel), [`integrations`](../integrations/) (platform services)
- **Downstream:** [`summaries`](../summaries/) (consumes messages for AI summarization)

## 🗄️ Models

### MessageBatch
```python
- id: UUID (PK)
- monitored_channel: ForeignKey(MonitoredChannel)
- batch_start_time: DateTimeField
- batch_end_time: DateTimeField
- message_count: IntegerField
- fetch_status: CharField (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- error_message: TextField (nullable)
- created_at, updated_at: DateTimeField
```

### Message
```python
- id: UUID (PK)
- batch: ForeignKey(MessageBatch)
- platform_message_id: CharField (unique per platform)
- author_id, author_name: CharField
- content: TextField
- message_type: CharField (TEXT, IMAGE, FILE, LINK, SYSTEM)
- timestamp: DateTimeField (platform message time)
- has_attachments: BooleanField
- attachments: JSONField (nullable)
- reactions: JSONField (nullable)
- is_reply: BooleanField
- reply_to_message_id: CharField (nullable)
- metadata: JSONField (platform-specific)
- created_at: DateTimeField
```

## 🔌 API Endpoints

### 1. List Message Batches
```
GET /api/messages/batches/
```
Query params: `monitored_channel`, `status`, `date_from`, `date_to`

### 2. Retrieve Batch Detail
```
GET /api/messages/batches/{id}/
```
Returns batch with message count and status

### 3. List Messages
```
GET /api/messages/
```
Query params: `batch`, `monitored_channel`, `author_id`, `message_type`, `search`

### 4. Retrieve Message Detail
```
GET /api/messages/{id}/
```

### 5. Trigger Message Fetch (Manual)
```
POST /api/messages/fetch/
Body: {"monitored_channel_id": "uuid", "start_time": "ISO8601", "end_time": "ISO8601"}
```

## ⚙️ Celery Tasks

### `fetch_messages_task(monitored_channel_id, start_time, end_time)`
- Creates MessageBatch with PENDING status
- Calls appropriate platform service (Discord/Telegram)
- Stores messages in bulk
- Updates batch status to COMPLETED/FAILED
- Updates MonitoredChannel.last_fetched_at

### `scheduled_message_fetch()`
- Runs every hour (configurable)
- Finds monitored channels due for fetch
- Triggers fetch_messages_task for each

## 🔐 Permissions
- `IsMessageOwner` - User owns the monitored channel
- `CanFetchMessages` - Email verified, has active connections

## 📁 Structure
```
messages/
├── models.py              # MessageBatch, Message
├── serializers.py         # API serializers
├── views.py               # ViewSets
├── urls.py                # URL routing
├── permissions.py         # Custom permissions
├── tasks.py               # Celery tasks
├── services/
│   ├── message_fetcher.py # Coordinates platform services
│   └── message_storage.py # Bulk message storage
└── tests/
    ├── test_models.py
    ├── test_views.py
    └── test_tasks.py
```

## 🚀 Implementation Phases

### Phase 1: Models & Migrations (2-3 hours)
- [ ] Create MessageBatch and Message models
- [ ] Run migrations
- [ ] Add to admin interface

### Phase 2: Services (3-4 hours)
- [ ] Message fetcher service (coordinates with integrations)
- [ ] Bulk message storage service
- [ ] Deduplication logic

### Phase 3: API Layer (2-3 hours)
- [ ] Serializers with nested relationships
- [ ] ViewSets with filtering
- [ ] Permissions

### Phase 4: Celery Tasks (2-3 hours)
- [ ] Fetch task with retry logic
- [ ] Scheduled fetch task
- [ ] Configure Celery beat

### Phase 5: Testing (2 hours)
- [ ] Model tests
- [ ] API tests
- [ ] Task tests

**Total Time:** 11-15 hours

## 🔄 Integration Flow

```
MonitoredChannel → Celery Task → Platform Service → MessageBatch → Messages → Summary Generation
```

## 📝 Key Considerations
- Implement pagination for large message sets
- Handle rate limits from Discord/Telegram APIs
- Deduplicate messages by platform_message_id
- Store attachments as URLs, not binary data
- Index timestamp and author_id for fast queries