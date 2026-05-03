# 📊 Monitoring App

The Monitoring app enables users to select and configure which channels from their connected platforms (Discord, Telegram) they want to monitor for automated message fetching and AI-powered summarization.

---

## 🎯 Purpose

After connecting platforms via the Integrations app, users need to specify which channels they want to actively monitor. The Monitoring app provides:

- **Channel Selection:** Choose specific channels from connected platforms
- **Fetch Configuration:** Set how often messages should be fetched (hourly, 6-hourly, daily)
- **Schedule Management:** Automatic scheduling of fetch and summarize tasks
- **Health Monitoring:** Track monitoring status and detect issues
- **Statistics:** View monitoring metrics and activity

---

## 🏗️ Architecture

### Models

#### MonitoredChannel
Represents a channel that a user has chosen to monitor.

**Key Fields:**
- `user` - The user who owns this monitoring configuration
- `channel` - Reference to Channel from Integrations app
- `is_active` - Whether monitoring is currently active
- `fetch_frequency` - How often to fetch (HOURLY, EVERY_6_HOURS, DAILY)
- `last_fetched_at` - Timestamp of last successful fetch
- `message_count` - Total messages fetched (denormalized)

**Key Methods:**
- `should_fetch_now()` - Check if fetch is due
- `calculate_next_fetch_time()` - Calculate next fetch time
- `activate()` / `deactivate()` - Control monitoring status

#### MonitoringSchedule
Manages the scheduling of fetch and summarize tasks.

**Key Fields:**
- `monitored_channel` - Reference to MonitoredChannel
- `schedule_type` - FETCH or SUMMARIZE
- `cron_expression` - Cron expression for scheduling
- `next_run_at` - When this schedule should run next
- `last_run_at` - When this schedule last ran

**Key Methods:**
- `calculate_next_run()` - Calculate next run time from cron
- `mark_run_complete()` - Update after successful run
- `is_due()` - Check if schedule should run now

---

## 🔌 API Endpoints

### Monitored Channels

```bash
# List monitored channels
GET /api/monitoring/channels/
Query params: ?is_active=true&platform=discord&frequency=HOURLY

# Add channel to monitoring
POST /api/monitoring/channels/
Body: {
  "channel_id": "uuid",
  "fetch_frequency": "HOURLY"
}

# Get monitoring details
GET /api/monitoring/channels/{id}/

# Update monitoring configuration
PATCH /api/monitoring/channels/{id}/
Body: {
  "fetch_frequency": "DAILY",
  "is_active": true
}

# Stop monitoring
DELETE /api/monitoring/channels/{id}/

# Toggle active status
POST /api/monitoring/channels/{id}/toggle/

# List available channels
GET /api/monitoring/channels/available/

# Get monitoring statistics
GET /api/monitoring/channels/stats/

# Bulk add channels
POST /api/monitoring/channels/bulk-add/
Body: {
  "channel_ids": ["uuid1", "uuid2"],
  "fetch_frequency": "HOURLY"
}
```

### Schedules

```bash
# List schedules
GET /api/monitoring/schedules/
Query params: ?monitored_channel_id=uuid&schedule_type=FETCH

# Get schedule details
GET /api/monitoring/schedules/{id}/
```

---

## 🔄 Background Tasks

### Celery Tasks

#### `check_due_schedules()`
**Frequency:** Every 5 minutes  
**Purpose:** Find and execute due schedules

```python
# Runs every 5 minutes via Celery Beat
# Finds schedules where next_run_at <= now
# Triggers appropriate tasks (fetch or summarize)
# Updates schedule run times
```

#### `sync_monitoring_schedules(monitored_channel_id)`
**Trigger:** When monitoring config changes  
**Purpose:** Synchronize schedules with monitoring configuration

```python
# Creates/updates FETCH and SUMMARIZE schedules
# Calculates next run times based on frequency
# Activates/deactivates schedules based on monitoring status
```

#### `health_check_monitoring()`
**Frequency:** Every 6 hours  
**Purpose:** Monitor health of all active monitoring

```python
# Checks for stale monitoring (no fetch in 2x frequency)
# Calculates health scores
# Sends alerts for issues
# Updates monitoring status
```

#### `cleanup_inactive_monitoring()`
**Frequency:** Weekly  
**Purpose:** Clean up old inactive monitoring

```python
# Archives monitoring ended > 30 days ago
# Cleans up orphaned schedules
# Maintains database health
```

---

## 🔐 Permissions

### IsMonitoringOwner
Ensures user owns the monitored channel they're trying to access.

```python
# Checks: obj.user == request.user
# Used on: Detail, Update, Delete operations
```

### CanManageMonitoring
Ensures user can manage monitoring (email verified, has active connection).

```python
# Checks:
# - User is authenticated
# - Email is verified
# - Has at least one active platform connection
# Used on: All monitoring operations
```

---

## 📊 Statistics & Analytics

### Monitoring Statistics
```json
{
  "total_monitored": 10,
  "active_monitored": 8,
  "total_messages": 1500,
  "fetch_success_rate": 0.95,
  "health_score": 0.92,
  "by_platform": {
    "discord": 6,
    "telegram": 4
  },
  "by_frequency": {
    "HOURLY": 3,
    "EVERY_6_HOURS": 4,
    "DAILY": 3
  }
}
```

### Health Scores
- **1.0 - Excellent:** All fetches successful, no delays
- **0.8-0.99 - Good:** Occasional delays, mostly successful
- **0.6-0.79 - Fair:** Some failures, needs attention
- **< 0.6 - Poor:** Frequent failures, requires intervention

---

## 🔗 Integration Points

### With Integrations App
- **Depends on:** Channel model
- **Validates:** User owns the connection for the channel
- **Uses:** Channel metadata (name, platform, connection status)

### With Messages App (Future)
- **Provides:** List of channels to fetch messages from
- **Provides:** Fetch frequency and schedule
- **Receives:** Message count updates

### With Summaries App (Future)
- **Provides:** Monitoring configuration for summarization
- **Provides:** Schedule for summary generation

---

## 🚀 Quick Start

### 1. Add Channel to Monitoring

```python
import requests

# Get available channels
response = requests.get(
    'http://localhost:8000/api/monitoring/channels/available/',
    headers={'Authorization': f'Bearer {access_token}'}
)
channels = response.json()['data']

# Add channel to monitoring
response = requests.post(
    'http://localhost:8000/api/monitoring/channels/',
    headers={'Authorization': f'Bearer {access_token}'},
    json={
        'channel_id': channels[0]['id'],
        'fetch_frequency': 'HOURLY'
    }
)
monitored = response.json()['data']
```

### 2. View Monitoring Status

```python
# List monitored channels
response = requests.get(
    'http://localhost:8000/api/monitoring/channels/',
    headers={'Authorization': f'Bearer {access_token}'}
)
monitored_channels = response.json()['data']['results']

# Get statistics
response = requests.get(
    'http://localhost:8000/api/monitoring/channels/stats/',
    headers={'Authorization': f'Bearer {access_token}'}
)
stats = response.json()['data']
```

### 3. Update Configuration

```python
# Change fetch frequency
response = requests.patch(
    f'http://localhost:8000/api/monitoring/channels/{monitored_id}/',
    headers={'Authorization': f'Bearer {access_token}'},
    json={'fetch_frequency': 'DAILY'}
)

# Pause monitoring
response = requests.post(
    f'http://localhost:8000/api/monitoring/channels/{monitored_id}/toggle/',
    headers={'Authorization': f'Bearer {access_token}'}
)
```

---

## 🧪 Testing

### Run Tests

```bash
# All monitoring tests
python manage.py test monitoring

# Specific test file
python manage.py test monitoring.tests.test_models
python manage.py test monitoring.tests.test_views
python manage.py test monitoring.tests.test_tasks

# With coverage
coverage run --source='monitoring' manage.py test monitoring
coverage report
```

### Test Coverage Goals
- **Models:** 90%+
- **Serializers:** 85%+
- **Views:** 85%+
- **Tasks:** 80%+
- **Overall:** 85%+

---

## 🛠️ Management Commands

### Sync Monitoring Schedules

```bash
# Sync all monitoring schedules
python manage.py sync_monitoring

# Sync for specific user
python manage.py sync_monitoring --user-id=<uuid>

# Sync for specific channel
python manage.py sync_monitoring --channel-id=<uuid>
```

### Check Monitoring Health

```bash
# Check health of all monitoring
python manage.py check_monitoring_health

# Check and fix issues
python manage.py check_monitoring_health --fix
```

---

## 📈 Performance Optimization

### Database Queries
```python
# Use select_related for ForeignKey
MonitoredChannel.objects.select_related('channel', 'channel__connection')

# Use prefetch_related for reverse ForeignKey
MonitoredChannel.objects.prefetch_related('monitoringschedule_set')

# Combine for complex queries
MonitoredChannel.objects.select_related(
    'channel', 'channel__connection'
).prefetch_related('monitoringschedule_set')
```

### Indexing
```python
# Indexes on MonitoredChannel
- (user, channel) - unique together
- is_active
- last_fetched_at
- fetch_frequency

# Indexes on MonitoringSchedule
- next_run_at
- is_active
- schedule_type
```

### Caching
```python
# Cache monitoring statistics (5 minutes)
# Cache available channels (15 minutes)
# Cache health scores (10 minutes)
```

---

## 🔍 Troubleshooting

### Issue: Monitoring not fetching messages

**Possible Causes:**
1. Monitoring is paused (is_active=False)
2. Schedule is not due yet
3. Platform connection is disconnected
4. Celery workers not running

**Solutions:**
```bash
# Check monitoring status
python manage.py shell
>>> from monitoring.models import MonitoredChannel
>>> mc = MonitoredChannel.objects.get(id='<uuid>')
>>> print(f"Active: {mc.is_active}, Last fetch: {mc.last_fetched_at}")

# Check schedules
>>> schedules = mc.monitoringschedule_set.all()
>>> for s in schedules:
...     print(f"{s.schedule_type}: next={s.next_run_at}, active={s.is_active}")

# Manually sync schedules
python manage.py sync_monitoring --channel-id=<uuid>

# Check Celery workers
celery -A Infobyte inspect active
```

### Issue: Stale monitoring detected

**Possible Causes:**
1. Fetch task failing
2. Platform API issues
3. Rate limiting
4. Invalid credentials

**Solutions:**
```bash
# Check error logs
python manage.py shell
>>> from monitoring.models import MonitoredChannel
>>> mc = MonitoredChannel.objects.get(id='<uuid>')
>>> # Check related connection status
>>> print(mc.channel.connection.status)

# Run health check
python manage.py check_monitoring_health --fix

# Manually trigger fetch
python manage.py sync_monitoring --channel-id=<uuid>
```

---

## 📚 Documentation

- **[Implementation Plan](docs/MONITORING_API_IMPLEMENTATION_PLAN.md)** - Detailed implementation phases
- **[Requirements](docs/MONITORING_API_REQUIREMENTS.md)** - Functional and non-functional requirements
- **[Flow Diagrams](docs/MONITORING_API_FLOW.md)** - Visual workflows and architecture
- **[API Documentation](docs/MONITORING_API_DOCUMENTATION.md)** - Complete API reference (after implementation)
- **[Quick Start Guide](docs/MONITORING_QUICK_START.md)** - Getting started guide (after implementation)

---

## 🎯 Implementation Status

### Phase 1: Foundation & Models ⏳
- [ ] MonitoredChannel model
- [ ] MonitoringSchedule model
- [ ] Admin interface
- [ ] Model tests

### Phase 2: Permissions & Serializers ⏳
- [ ] Custom permissions
- [ ] Serializers
- [ ] Validation logic
- [ ] Serializer tests

### Phase 3: Core API Views ⏳
- [ ] CRUD endpoints
- [ ] Filtering and pagination
- [ ] View tests

### Phase 4: Schedule Management ⏳
- [ ] Schedule utilities
- [ ] Cron parsing
- [ ] Schedule synchronization
- [ ] Utility tests

### Phase 5: Background Tasks ⏳
- [ ] Celery tasks
- [ ] Periodic scheduling
- [ ] Task tests

### Phase 6: Statistics & Analytics ⏳
- [ ] Statistics aggregation
- [ ] Analytics endpoints
- [ ] Analytics tests

### Phase 7: Integration & Configuration ⏳
- [ ] Django settings
- [ ] URL routing
- [ ] Management commands

### Phase 8: Testing & Documentation ⏳
- [ ] Complete test coverage
- [ ] API documentation
- [ ] User guides

---

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] Custom cron expressions for advanced users
- [ ] Monitoring templates (save and reuse configurations)
- [ ] Channel groups (monitor multiple channels as one)
- [ ] Advanced filtering (by keywords, authors, etc.)
- [ ] Monitoring presets (quick setup for common scenarios)

### Phase 3 Features
- [ ] Real-time monitoring status updates (WebSocket)
- [ ] Predictive scheduling (ML-based optimal fetch times)
- [ ] Cross-platform monitoring (monitor related channels together)
- [ ] Monitoring recommendations (suggest channels to monitor)
- [ ] Advanced analytics and reporting

---

## 📊 Metrics

### Target Metrics
- **API Response Time:** < 200ms (list), < 100ms (detail)
- **Test Coverage:** 85%+
- **Schedule Accuracy:** 99%+ (runs within 1 minute of scheduled time)
- **Health Check Success:** 95%+
- **User Satisfaction:** 4.5/5+

### Current Metrics
- **Total Files:** 25+ (planned)
- **Total Lines:** ~4,500+ (planned)
- **Models:** 2
- **API Endpoints:** 10+
- **Background Tasks:** 4
- **Tests:** 60+ (planned)

---

## 🤝 Contributing

When contributing to the Monitoring app:

1. Follow existing code patterns from Integrations and Accounts apps
2. Write tests for all new functionality
3. Update documentation for API changes
4. Use type hints and docstrings
5. Follow Django and DRF best practices

---

## 📝 License

This project is part of ChatSift and follows the same license.

---

# Made with Bob

Built with ❤️ by Bob, your AI coding assistant.