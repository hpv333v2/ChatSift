# 🛠️ Monitoring APIs - Implementation Plan

## 📋 Overview

The Monitoring app enables users to select which channels from their connected platforms they want to monitor, configure fetch frequencies, and manage monitoring schedules. This app bridges the Integrations app (platform connections) with the Messages app (message fetching).

**Dependencies:**
- ✅ Accounts app (User model)
- ✅ Integrations app (Channel model)
- ⏳ Messages app (will consume monitoring data)

**Estimated Total Time:** 18-22 hours across 8 phases

---

## 📋 Implementation Phases

### Phase 1: Foundation & Models (Priority: Critical)
**Estimated Time:** 2-3 hours

#### Tasks:
1. ✅ Create monitoring app structure (already exists)
2. ⬜ Define MonitoredChannel model
   - User-channel relationship
   - Monitoring configuration (frequency, active status)
   - Tracking fields (last_fetched_at, start/end dates)
3. ⬜ Define MonitoringSchedule model
   - Schedule management for fetch/summarize tasks
   - Cron expression support
   - Next run calculation
4. ⬜ Add model methods and properties
5. ⬜ Create and run migrations
6. ⬜ Add models to admin interface
7. ⬜ Write model unit tests

#### Files to Create:
- `models.py` - Database models (~250 lines)
- `admin.py` - Admin interface (~60 lines)
- `migrations/0001_initial.py` - Initial migration (auto-generated)
- `tests/test_models.py` - Model tests (~200 lines)

#### Model Details:

**MonitoredChannel:**
```python
- id: UUID (PK)
- user: ForeignKey(User, on_delete=CASCADE)
- channel: ForeignKey(Channel, on_delete=CASCADE)
- is_active: BooleanField (default=True)
- monitoring_start_date: DateField (auto_now_add)
- monitoring_end_date: DateField (nullable, for pausing)
- fetch_frequency: CharField (HOURLY, EVERY_6_HOURS, DAILY)
- last_fetched_at: DateTimeField (nullable)
- message_count: IntegerField (default=0, denormalized)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)

Indexes:
- (user, channel) - unique together
- is_active
- last_fetched_at
- fetch_frequency

Methods:
- should_fetch_now() -> bool
- calculate_next_fetch_time() -> datetime
- get_monitoring_duration() -> timedelta
- activate() / deactivate()
```

**MonitoringSchedule:**
```python
- id: UUID (PK)
- monitored_channel: ForeignKey(MonitoredChannel, on_delete=CASCADE)
- schedule_type: CharField (FETCH, SUMMARIZE)
- cron_expression: CharField (max_length=100)
- is_active: BooleanField (default=True)
- last_run_at: DateTimeField (nullable)
- next_run_at: DateTimeField
- run_count: IntegerField (default=0)
- failure_count: IntegerField (default=0)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)

Indexes:
- next_run_at
- is_active
- schedule_type

Methods:
- calculate_next_run() -> datetime
- mark_run_complete()
- mark_run_failed()
- is_due() -> bool
```

---

### Phase 2: Permissions & Serializers (Priority: High)
**Estimated Time:** 2-3 hours

#### Tasks:
1. ⬜ Create IsMonitoringOwner permission
2. ⬜ Create CanManageMonitoring permission
3. ⬜ Create MonitoredChannelSerializer
4. ⬜ Create MonitoredChannelListSerializer (optimized)
5. ⬜ Create MonitoredChannelCreateSerializer
6. ⬜ Create MonitoredChannelUpdateSerializer
7. ⬜ Create MonitoringScheduleSerializer
8. ⬜ Create MonitoringStatsSerializer
9. ⬜ Write serializer validation tests
10. ⬜ Write permission tests

#### Files to Create:
- `permissions.py` - Custom permissions (~40 lines)
- `serializers.py` - API serializers (~300 lines)
- `tests/test_permissions.py` - Permission tests (~150 lines)
- `tests/test_serializers.py` - Serializer tests (~250 lines)

#### Serializer Details:

**MonitoredChannelSerializer:**
- Full representation with nested channel details
- Computed fields: monitoring_duration, next_fetch_time, status
- Read-only fields: message_count, last_fetched_at

**MonitoredChannelCreateSerializer:**
- Validates channel belongs to user's connection
- Validates channel not already monitored
- Sets default fetch_frequency

**MonitoredChannelUpdateSerializer:**
- Allows updating: is_active, fetch_frequency, monitoring_end_date
- Validates frequency changes
- Recalculates schedules on frequency change

---

### Phase 3: Core API Views (Priority: High)
**Estimated Time:** 4-5 hours

#### Tasks:
1. ⬜ Create MonitoredChannelListView (list user's monitored channels)
2. ⬜ Create MonitoredChannelCreateView (add channel to monitoring)
3. ⬜ Create MonitoredChannelDetailView (get monitoring details)
4. ⬜ Create MonitoredChannelUpdateView (update monitoring config)
5. ⬜ Create MonitoredChannelDeleteView (stop monitoring)
6. ⬜ Create MonitoredChannelToggleView (quick activate/deactivate)
7. ⬜ Create AvailableChannelsView (list channels available for monitoring)
8. ⬜ Add filtering, searching, and pagination
9. ⬜ Write view tests

#### Files to Create:
- `views.py` - API views (~400 lines)
- `urls.py` - URL configuration (~60 lines)
- `tests/test_views.py` - View tests (~400 lines)

#### API Endpoints:

```
GET    /api/monitoring/channels/              # List monitored channels
POST   /api/monitoring/channels/              # Add channel to monitoring
GET    /api/monitoring/channels/{id}/         # Get monitoring details
PATCH  /api/monitoring/channels/{id}/         # Update monitoring config
DELETE /api/monitoring/channels/{id}/         # Stop monitoring
POST   /api/monitoring/channels/{id}/toggle/  # Toggle active status
GET    /api/monitoring/channels/available/    # List available channels
GET    /api/monitoring/channels/stats/        # Get monitoring statistics
POST   /api/monitoring/channels/bulk-add/     # Add multiple channels
POST   /api/monitoring/channels/bulk-update/  # Update multiple channels
```

---

### Phase 4: Schedule Management (Priority: High)
**Estimated Time:** 3-4 hours

#### Tasks:
1. ⬜ Create schedule calculation utilities
2. ⬜ Implement cron expression parser
3. ⬜ Create schedule synchronization logic
4. ⬜ Implement schedule views (list, detail, update)
5. ⬜ Add schedule validation
6. ⬜ Write schedule tests

#### Files to Create:
- `utils.py` - Schedule utilities (~200 lines)
- `schedule_views.py` - Schedule management views (~250 lines)
- `tests/test_utils.py` - Utility tests (~150 lines)
- `tests/test_schedule_views.py` - Schedule view tests (~200 lines)

#### Schedule Utilities:

**Functions:**
- `calculate_next_run(cron_expression, from_time)` - Calculate next run time
- `frequency_to_cron(frequency)` - Convert frequency to cron expression
- `sync_schedules(monitored_channel)` - Sync schedules with monitoring config
- `get_due_schedules()` - Get schedules that should run now
- `validate_cron_expression(expression)` - Validate cron syntax

---

### Phase 5: Background Tasks (Priority: High)
**Estimated Time:** 3-4 hours

#### Tasks:
1. ⬜ Create schedule sync task (when monitoring config changes)
2. ⬜ Create schedule checker task (find due schedules)
3. ⬜ Create monitoring health check task
4. ⬜ Create inactive monitoring cleanup task
5. ⬜ Set up periodic task scheduling
6. ⬜ Add task retry logic
7. ⬜ Write task tests

#### Files to Create:
- `tasks.py` - Celery tasks (~350 lines)
- `tests/test_tasks.py` - Task tests (~300 lines)

#### Celery Tasks:

**sync_monitoring_schedules(monitored_channel_id)**
- Triggered when monitoring config changes
- Creates/updates FETCH and SUMMARIZE schedules
- Calculates next run times

**check_due_schedules()**
- Runs every 5 minutes
- Finds schedules where next_run_at <= now
- Triggers appropriate tasks (fetch or summarize)
- Updates schedule run times

**health_check_monitoring()**
- Runs every 6 hours
- Checks for stale monitoring (no fetch in 2x frequency)
- Sends alerts for failed monitoring
- Updates monitoring status

**cleanup_inactive_monitoring()**
- Runs weekly
- Archives monitoring ended > 30 days ago
- Cleans up orphaned schedules

---

### Phase 6: Statistics & Analytics (Priority: Medium)
**Estimated Time:** 2-3 hours

#### Tasks:
1. ⬜ Create monitoring statistics aggregation
2. ⬜ Implement dashboard data views
3. ⬜ Create monitoring activity timeline
4. ⬜ Add monitoring health metrics
5. ⬜ Write analytics tests

#### Files to Create:
- `analytics.py` - Statistics and analytics (~200 lines)
- `dashboard_views.py` - Dashboard API views (~150 lines)
- `tests/test_analytics.py` - Analytics tests (~150 lines)

#### Analytics Features:

**MonitoringStats:**
- Total monitored channels (active/inactive)
- Messages fetched (total, by platform, by frequency)
- Monitoring health score
- Average fetch success rate
- Most active channels

**MonitoringTimeline:**
- Recent monitoring activities
- Fetch history
- Configuration changes
- Error events

---

### Phase 7: Integration & Configuration (Priority: High)
**Estimated Time:** 1-2 hours

#### Tasks:
1. ⬜ Update Django settings
2. ⬜ Add app to INSTALLED_APPS
3. ⬜ Configure URL routing
4. ⬜ Update Celery beat schedule
5. ⬜ Create management commands
6. ⬜ Update requirements.txt (if needed)

#### Files to Update/Create:
- `backend/Infobyte/settings.py` - Add monitoring app
- `backend/Infobyte/urls.py` - Include monitoring URLs
- `backend/Infobyte/celery.py` - Add monitoring tasks to beat schedule
- `management/commands/sync_monitoring.py` - Manual sync command (~150 lines)
- `management/commands/check_monitoring_health.py` - Health check command (~100 lines)

#### Management Commands:

**sync_monitoring**
```bash
python manage.py sync_monitoring [--user-id=<id>] [--channel-id=<id>]
```
- Manually sync monitoring schedules
- Useful for debugging or bulk updates

**check_monitoring_health**
```bash
python manage.py check_monitoring_health [--fix]
```
- Check monitoring health
- Optionally fix issues (reactivate stale monitoring)

---

### Phase 8: Testing & Documentation (Priority: Medium)
**Estimated Time:** 2-3 hours

#### Tasks:
1. ⬜ Run all tests and ensure coverage (target: 85%+)
2. ⬜ Create API documentation
3. ⬜ Create quick start guide
4. ⬜ Create monitoring configuration guide
5. ⬜ Create troubleshooting guide
6. ⬜ Update main README

#### Files to Create:
- `docs/MONITORING_API_DOCUMENTATION.md` (~500 lines)
- `docs/MONITORING_QUICK_START.md` (~300 lines)
- `docs/MONITORING_CONFIGURATION_GUIDE.md` (~250 lines)
- `docs/MONITORING_TROUBLESHOOTING.md` (~200 lines)
- `README.md` (~350 lines)
- `IMPLEMENTATION_SUMMARY.md` (after completion)

---

## 🔧 Technical Implementation Details

### 1. Frequency to Cron Conversion

```python
# utils.py
FREQUENCY_CRON_MAP = {
    'HOURLY': '0 * * * *',           # Every hour at minute 0
    'EVERY_6_HOURS': '0 */6 * * *',  # Every 6 hours at minute 0
    'DAILY': '0 0 * * *',            # Every day at midnight
}

def frequency_to_cron(frequency):
    """Convert fetch frequency to cron expression."""
    return FREQUENCY_CRON_MAP.get(frequency, '0 * * * *')
```

### 2. Next Run Calculation

```python
# utils.py
from croniter import croniter
from django.utils import timezone

def calculate_next_run(cron_expression, from_time=None):
    """Calculate next run time from cron expression."""
    if from_time is None:
        from_time = timezone.now()
    
    cron = croniter(cron_expression, from_time)
    return cron.get_next(datetime)
```

### 3. Schedule Synchronization

```python
# utils.py
def sync_schedules(monitored_channel):
    """Sync schedules with monitoring configuration."""
    if not monitored_channel.is_active:
        # Deactivate all schedules
        monitored_channel.monitoringschedule_set.update(is_active=False)
        return
    
    # Get or create FETCH schedule
    fetch_schedule, created = MonitoringSchedule.objects.get_or_create(
        monitored_channel=monitored_channel,
        schedule_type='FETCH',
        defaults={
            'cron_expression': frequency_to_cron(monitored_channel.fetch_frequency),
            'next_run_at': calculate_next_run(
                frequency_to_cron(monitored_channel.fetch_frequency)
            ),
        }
    )
    
    if not created:
        # Update existing schedule
        fetch_schedule.cron_expression = frequency_to_cron(
            monitored_channel.fetch_frequency
        )
        fetch_schedule.next_run_at = calculate_next_run(
            fetch_schedule.cron_expression
        )
        fetch_schedule.is_active = True
        fetch_schedule.save()
```

### 4. Permission Implementation

```python
# permissions.py
from rest_framework.permissions import BasePermission

class IsMonitoringOwner(BasePermission):
    """Ensure user owns the monitored channel."""
    message = "You don't have permission to access this monitoring configuration."
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanManageMonitoring(BasePermission):
    """Ensure user can manage monitoring (email verified, active connection)."""
    message = "You must have an active platform connection to manage monitoring."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.email_verified:
            self.message = "Email verification required to manage monitoring."
            return False
        
        # Check if user has at least one active connection
        from integrations.models import PlatformConnection
        has_connection = PlatformConnection.objects.filter(
            user=request.user,
            status='CONNECTED'
        ).exists()
        
        if not has_connection:
            self.message = "You must connect a platform before monitoring channels."
            return False
        
        return True
```

### 5. View Implementation Pattern

```python
# views.py
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMonitoringOwner, CanManageMonitoring
from .serializers import MonitoredChannelSerializer, MonitoredChannelCreateSerializer

class MonitoredChannelListCreateView(generics.ListCreateAPIView):
    """List monitored channels or add new channel to monitoring."""
    permission_classes = [IsAuthenticated, CanManageMonitoring]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MonitoredChannelCreateSerializer
        return MonitoredChannelSerializer
    
    def get_queryset(self):
        queryset = MonitoredChannel.objects.filter(
            user=self.request.user
        ).select_related('channel', 'channel__connection')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by platform
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(channel__connection__platform=platform)
        
        # Filter by frequency
        frequency = self.request.query_params.get('frequency')
        if frequency:
            queryset = queryset.filter(fetch_frequency=frequency)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        monitored_channel = serializer.save(user=self.request.user)
        
        # Sync schedules after creation
        from .utils import sync_schedules
        sync_schedules(monitored_channel)
```

---

## 📦 Dependencies to Add

```txt
# Cron expression parsing
croniter==2.0.1

# Timezone handling (already in Django)
pytz==2023.3
```

---

## 🧪 Testing Strategy

### Unit Tests
- Model validation and constraints
- Serializer validation
- Permission logic
- Utility functions (cron parsing, schedule calculation)
- Schedule synchronization

### Integration Tests
- Complete monitoring flow (add, update, delete)
- API endpoint responses
- Schedule creation and updates
- Error handling
- Permission enforcement

### Mock External Dependencies
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, patch
from django.utils import timezone

@pytest.fixture
def mock_celery_task():
    with patch('monitoring.tasks.sync_monitoring_schedules.delay') as mock:
        yield mock

@pytest.fixture
def sample_monitored_channel(db, user, channel):
    from monitoring.models import MonitoredChannel
    return MonitoredChannel.objects.create(
        user=user,
        channel=channel,
        fetch_frequency='HOURLY',
        is_active=True
    )
```

---

## 🔐 Security Checklist

- [ ] User can only monitor channels from their own connections
- [ ] Permission checks on all endpoints
- [ ] Input validation on all user inputs
- [ ] Rate limiting on API endpoints
- [ ] Audit logging for monitoring changes
- [ ] Secure error messages (no sensitive data leaks)
- [ ] CSRF protection on state-changing operations

---

## 📊 Success Metrics

- [ ] All models created and migrated
- [ ] 85%+ test coverage
- [ ] All API endpoints functional
- [ ] Schedule synchronization working
- [ ] Background tasks operational
- [ ] Documentation complete
- [ ] No security vulnerabilities
- [ ] Integration with integrations app verified

---

## 🚀 Deployment Checklist

- [ ] Database migrations applied
- [ ] Celery workers running
- [ ] Celery beat scheduler running
- [ ] Monitoring tasks scheduled
- [ ] Rate limiting configured
- [ ] Monitoring and logging set up
- [ ] API documentation published
- [ ] Health check endpoints working

---

## 📝 Next Steps After Implementation

1. **Messages App** - Fetch and store messages from monitored channels
2. **Summaries App** - Generate AI summaries of fetched messages
3. **Notifications App** - Deliver summaries to users

---

## 🔄 Integration Points

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

## 🎯 Key Features

### Core Features
- ✅ Add channels to monitoring
- ✅ Configure fetch frequency (hourly, 6-hourly, daily)
- ✅ Activate/deactivate monitoring
- ✅ View monitoring statistics
- ✅ Automatic schedule management
- ✅ Health monitoring
- ✅ Bulk operations

### Advanced Features
- ✅ Custom cron expressions (future)
- ✅ Monitoring templates (future)
- ✅ Advanced filtering and search
- ✅ Monitoring analytics
- ✅ Activity timeline

---

## 📐 Architecture Decisions

### 1. Separate Schedule Model
**Decision:** Create separate MonitoringSchedule model  
**Rationale:** Allows flexible scheduling, supports multiple schedule types (fetch, summarize), easier to query due schedules  
**Trade-off:** Additional complexity, but better separation of concerns

### 2. Cron-Based Scheduling
**Decision:** Use cron expressions for scheduling  
**Rationale:** Standard, flexible, well-understood, integrates with Celery Beat  
**Trade-off:** Requires croniter library, but provides maximum flexibility

### 3. Denormalized Message Count
**Decision:** Store message_count on MonitoredChannel  
**Rationale:** Faster queries for statistics, avoids expensive COUNT queries  
**Trade-off:** Must keep in sync, but worth it for performance

### 4. Soft Delete Pattern
**Decision:** Use monitoring_end_date instead of hard delete  
**Rationale:** Preserves history, allows reactivation, supports analytics  
**Trade-off:** More complex queries, but better data retention

---

## 🔍 Key Implementation Notes

1. **Schedule Synchronization:** Always sync schedules when monitoring config changes
2. **Timezone Handling:** All times stored in UTC, converted for display
3. **Frequency Validation:** Validate frequency changes don't create conflicts
4. **Orphan Prevention:** Cascade delete schedules when monitoring is deleted
5. **Performance:** Use select_related for channel and connection queries
6. **Idempotency:** All schedule operations should be idempotent
7. **Error Recovery:** Failed schedule runs should not block future runs

---

## 📊 Estimated Code Statistics

- **Total Files:** 25+ files
- **Total Lines:** ~4,500+ lines
- **Models:** 2 (MonitoredChannel, MonitoringSchedule)
- **Serializers:** 8
- **Views:** 10+ API endpoints
- **Tasks:** 4 Celery tasks
- **Tests:** 60+ tests across 8 test files
- **Management Commands:** 2
- **Documentation:** 5 comprehensive guides

---

## 🎓 Learning Outcomes

After implementing this app, you will have learned:
- Advanced Django model relationships
- Cron-based scheduling with Celery
- Complex permission systems
- Schedule calculation and management
- Denormalization strategies
- Background task orchestration
- API design for configuration management

---

# Made with Bob

Built with ❤️ by Bob, your AI coding assistant.