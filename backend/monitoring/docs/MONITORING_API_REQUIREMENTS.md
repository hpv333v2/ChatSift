# 📋 Monitoring API - Requirements Document

## 🎯 Purpose

The Monitoring API enables users to select and configure which channels from their connected platforms (Discord, Telegram) they want to monitor for message fetching and summarization.

---

## 👥 User Stories

### As a User, I want to:

1. **View Available Channels**
   - See all channels from my connected platforms
   - Filter channels by platform (Discord/Telegram)
   - See which channels are already being monitored
   - View channel metadata (name, type, member count)

2. **Add Channels to Monitoring**
   - Select one or multiple channels to monitor
   - Choose fetch frequency (hourly, 6-hourly, daily)
   - Set monitoring start date
   - Optionally set monitoring end date

3. **Manage Monitored Channels**
   - View list of all my monitored channels
   - See monitoring status (active/inactive)
   - View last fetch time and message count
   - Update fetch frequency
   - Pause/resume monitoring
   - Stop monitoring (remove channel)

4. **View Monitoring Statistics**
   - See total monitored channels
   - View messages fetched per channel
   - See monitoring health status
   - View fetch success rate
   - See upcoming fetch schedules

5. **Troubleshoot Issues**
   - View monitoring errors
   - See failed fetch attempts
   - Manually trigger channel sync
   - View monitoring activity log

---

## 🔧 Functional Requirements

### FR1: Channel Selection
- **FR1.1:** System must list all channels from user's active platform connections
- **FR1.2:** System must prevent monitoring the same channel twice
- **FR1.3:** System must validate user owns the connection for the channel
- **FR1.4:** System must support bulk channel addition

### FR2: Monitoring Configuration
- **FR2.1:** System must support three fetch frequencies: HOURLY, EVERY_6_HOURS, DAILY
- **FR2.2:** System must allow users to change fetch frequency
- **FR2.3:** System must automatically create schedules based on frequency
- **FR2.4:** System must recalculate schedules when frequency changes
- **FR2.5:** System must support monitoring start and end dates

### FR3: Schedule Management
- **FR3.1:** System must create FETCH schedule for each monitored channel
- **FR3.2:** System must create SUMMARIZE schedule for each monitored channel
- **FR3.3:** System must calculate next run time using cron expressions
- **FR3.4:** System must track schedule execution history
- **FR3.5:** System must handle schedule failures gracefully

### FR4: Monitoring Status
- **FR4.1:** System must track monitoring active/inactive status
- **FR4.2:** System must record last fetch timestamp
- **FR4.3:** System must count total messages fetched
- **FR4.4:** System must detect stale monitoring (no fetch in 2x frequency)
- **FR4.5:** System must provide health status for each monitored channel

### FR5: Background Processing
- **FR5.1:** System must check for due schedules every 5 minutes
- **FR5.2:** System must trigger fetch tasks for due schedules
- **FR5.3:** System must update schedule run times after execution
- **FR5.4:** System must perform health checks every 6 hours
- **FR5.5:** System must cleanup inactive monitoring weekly

### FR6: Statistics & Analytics
- **FR6.1:** System must provide monitoring overview statistics
- **FR6.2:** System must track fetch success/failure rates
- **FR6.3:** System must show monitoring activity timeline
- **FR6.4:** System must calculate monitoring health scores
- **FR6.5:** System must identify most active channels

### FR7: Permissions & Security
- **FR7.1:** Users must be authenticated to access monitoring APIs
- **FR7.2:** Users must have verified email to manage monitoring
- **FR7.3:** Users must have active platform connection to add monitoring
- **FR7.4:** Users can only manage their own monitored channels
- **FR7.5:** System must validate all user inputs

---

## 🚫 Non-Functional Requirements

### NFR1: Performance
- **NFR1.1:** API response time must be < 200ms for list operations
- **NFR1.2:** API response time must be < 100ms for detail operations
- **NFR1.3:** Schedule calculation must complete in < 50ms
- **NFR1.4:** Bulk operations must handle up to 50 channels
- **NFR1.5:** Database queries must use proper indexing

### NFR2: Scalability
- **NFR2.1:** System must support 10,000+ monitored channels per user
- **NFR2.2:** System must handle 100+ concurrent API requests
- **NFR2.3:** Background tasks must process 1,000+ schedules per minute
- **NFR2.4:** System must support horizontal scaling of workers

### NFR3: Reliability
- **NFR3.1:** System uptime must be 99.9%
- **NFR3.2:** Failed tasks must retry with exponential backoff
- **NFR3.3:** System must recover from database connection failures
- **NFR3.4:** Schedule execution must be idempotent
- **NFR3.5:** Data consistency must be maintained across failures

### NFR4: Security
- **NFR4.1:** All API endpoints must require authentication
- **NFR4.2:** Permission checks must be enforced on all operations
- **NFR4.3:** Input validation must prevent injection attacks
- **NFR4.4:** Rate limiting must prevent abuse
- **NFR4.5:** Audit logs must track all monitoring changes

### NFR5: Maintainability
- **NFR5.1:** Code must have 85%+ test coverage
- **NFR5.2:** All functions must have docstrings
- **NFR5.3:** API must follow RESTful conventions
- **NFR5.4:** Error messages must be clear and actionable
- **NFR5.5:** Code must follow Django best practices

### NFR6: Usability
- **NFR6.1:** API responses must be consistent and well-structured
- **NFR6.2:** Error messages must be user-friendly
- **NFR6.3:** API documentation must be comprehensive
- **NFR6.4:** Filtering and pagination must be intuitive
- **NFR6.5:** Bulk operations must provide detailed feedback

---

## 📊 Data Requirements

### DR1: MonitoredChannel Model
```python
Required Fields:
- user (ForeignKey to User)
- channel (ForeignKey to Channel)
- is_active (Boolean)
- fetch_frequency (Choice: HOURLY, EVERY_6_HOURS, DAILY)
- monitoring_start_date (Date)

Optional Fields:
- monitoring_end_date (Date)
- last_fetched_at (DateTime)
- message_count (Integer, default=0)

Computed Fields:
- monitoring_duration (TimeDelta)
- next_fetch_time (DateTime)
- status (String: active, paused, ended, stale)
- health_score (Float: 0.0-1.0)

Constraints:
- Unique together: (user, channel)
- Index on: is_active, last_fetched_at, fetch_frequency
```

### DR2: MonitoringSchedule Model
```python
Required Fields:
- monitored_channel (ForeignKey to MonitoredChannel)
- schedule_type (Choice: FETCH, SUMMARIZE)
- cron_expression (String)
- is_active (Boolean)
- next_run_at (DateTime)

Optional Fields:
- last_run_at (DateTime)
- run_count (Integer, default=0)
- failure_count (Integer, default=0)

Computed Fields:
- is_due (Boolean)
- time_until_next_run (TimeDelta)
- success_rate (Float: 0.0-1.0)

Constraints:
- Index on: next_run_at, is_active, schedule_type
```

---

## 🔌 API Endpoints

### Monitored Channels

#### List Monitored Channels
```
GET /api/monitoring/channels/
Query Parameters:
  - is_active: boolean (filter by active status)
  - platform: string (filter by platform: discord, telegram)
  - frequency: string (filter by frequency)
  - page: integer (pagination)
  - page_size: integer (pagination)
Response: 200 OK
{
  "status": "success",
  "data": {
    "count": 10,
    "next": "...",
    "previous": null,
    "results": [...]
  }
}
```

#### Add Channel to Monitoring
```
POST /api/monitoring/channels/
Body:
{
  "channel_id": "uuid",
  "fetch_frequency": "HOURLY",
  "monitoring_end_date": "2024-12-31" (optional)
}
Response: 201 Created
{
  "status": "success",
  "data": {...}
}
```

#### Get Monitoring Details
```
GET /api/monitoring/channels/{id}/
Response: 200 OK
{
  "status": "success",
  "data": {...}
}
```

#### Update Monitoring Configuration
```
PATCH /api/monitoring/channels/{id}/
Body:
{
  "fetch_frequency": "DAILY",
  "is_active": true
}
Response: 200 OK
{
  "status": "success",
  "data": {...}
}
```

#### Stop Monitoring
```
DELETE /api/monitoring/channels/{id}/
Response: 204 No Content
```

#### Toggle Monitoring Status
```
POST /api/monitoring/channels/{id}/toggle/
Response: 200 OK
{
  "status": "success",
  "data": {
    "is_active": false
  }
}
```

### Available Channels

#### List Available Channels
```
GET /api/monitoring/channels/available/
Query Parameters:
  - platform: string (filter by platform)
  - exclude_monitored: boolean (default: true)
Response: 200 OK
{
  "status": "success",
  "data": [...]
}
```

### Bulk Operations

#### Bulk Add Channels
```
POST /api/monitoring/channels/bulk-add/
Body:
{
  "channel_ids": ["uuid1", "uuid2", ...],
  "fetch_frequency": "HOURLY"
}
Response: 201 Created
{
  "status": "success",
  "data": {
    "added": 5,
    "failed": 0,
    "results": [...]
  }
}
```

#### Bulk Update Channels
```
POST /api/monitoring/channels/bulk-update/
Body:
{
  "channel_ids": ["uuid1", "uuid2", ...],
  "updates": {
    "fetch_frequency": "DAILY"
  }
}
Response: 200 OK
{
  "status": "success",
  "data": {
    "updated": 5,
    "failed": 0
  }
}
```

### Statistics

#### Get Monitoring Statistics
```
GET /api/monitoring/channels/stats/
Response: 200 OK
{
  "status": "success",
  "data": {
    "total_monitored": 10,
    "active_monitored": 8,
    "total_messages": 1500,
    "fetch_success_rate": 0.95,
    "health_score": 0.92,
    "by_platform": {...},
    "by_frequency": {...}
  }
}
```

### Schedules

#### List Schedules
```
GET /api/monitoring/schedules/
Query Parameters:
  - monitored_channel_id: uuid
  - schedule_type: string (FETCH, SUMMARIZE)
  - is_due: boolean
Response: 200 OK
{
  "status": "success",
  "data": [...]
}
```

#### Get Schedule Details
```
GET /api/monitoring/schedules/{id}/
Response: 200 OK
{
  "status": "success",
  "data": {...}
}
```

---

## 🔄 Business Logic

### BL1: Adding Channel to Monitoring
1. Validate user is authenticated and email verified
2. Validate user has active connection for the channel
3. Check channel is not already monitored by user
4. Create MonitoredChannel record
5. Create FETCH schedule with cron expression
6. Create SUMMARIZE schedule (daily at midnight)
7. Calculate next run times
8. Return success response

### BL2: Updating Fetch Frequency
1. Validate user owns the monitored channel
2. Update fetch_frequency field
3. Update FETCH schedule cron expression
4. Recalculate next_run_at
5. Keep SUMMARIZE schedule unchanged
6. Return updated monitoring configuration

### BL3: Pausing/Resuming Monitoring
1. Validate user owns the monitored channel
2. Toggle is_active status
3. If pausing: deactivate all schedules
4. If resuming: reactivate schedules, recalculate next run times
5. Return updated status

### BL4: Schedule Execution
1. Find all schedules where next_run_at <= now and is_active = true
2. For each schedule:
   - If FETCH: trigger message fetch task
   - If SUMMARIZE: trigger summary generation task
3. Update last_run_at to now
4. Calculate and update next_run_at
5. Increment run_count
6. If task fails: increment failure_count

### BL5: Health Check
1. Find all active monitored channels
2. For each channel:
   - Calculate expected fetch interval (frequency * 2)
   - If last_fetched_at is older than interval: mark as stale
   - Calculate health score based on fetch success rate
3. Send alerts for unhealthy monitoring
4. Update monitoring status

---

## 🧪 Test Requirements

### Unit Tests (Target: 85% coverage)
- Model validation and constraints
- Serializer validation
- Permission logic
- Utility functions (cron parsing, schedule calculation)
- Business logic methods

### Integration Tests
- Complete monitoring flow (add, update, delete)
- API endpoint responses
- Schedule creation and synchronization
- Error handling
- Permission enforcement

### Performance Tests
- API response times under load
- Schedule calculation performance
- Bulk operation performance
- Database query optimization

---

## 📈 Success Criteria

### Phase 1 Success Criteria
- [ ] Models created and migrated
- [ ] Admin interface functional
- [ ] Model tests passing (20+ tests)

### Phase 2 Success Criteria
- [ ] Serializers implemented and tested
- [ ] Permissions implemented and tested
- [ ] Validation working correctly

### Phase 3 Success Criteria
- [ ] All API endpoints functional
- [ ] CRUD operations working
- [ ] Filtering and pagination working

### Phase 4 Success Criteria
- [ ] Schedule calculation working
- [ ] Schedule synchronization working
- [ ] Cron expression parsing working

### Phase 5 Success Criteria
- [ ] Background tasks implemented
- [ ] Celery beat schedule configured
- [ ] Task retry logic working

### Phase 6 Success Criteria
- [ ] Statistics aggregation working
- [ ] Analytics endpoints functional
- [ ] Dashboard data available

### Phase 7 Success Criteria
- [ ] Django settings updated
- [ ] URL routing configured
- [ ] Management commands working

### Phase 8 Success Criteria
- [ ] 85%+ test coverage achieved
- [ ] All documentation complete
- [ ] API documentation published

---

## 🚧 Constraints & Assumptions

### Constraints
- Must integrate with existing Integrations app
- Must use Django ORM (no raw SQL)
- Must follow existing project patterns
- Must maintain backward compatibility
- Must support PostgreSQL and SQLite

### Assumptions
- Users have already connected platforms via Integrations app
- Celery and Redis are properly configured
- Users understand cron expressions (for advanced features)
- Message fetching will be handled by Messages app
- Summarization will be handled by Summaries app

---

## 🔮 Future Enhancements

### Phase 2 Features (Post-MVP)
- Custom cron expressions for advanced users
- Monitoring templates (save and reuse configurations)
- Channel groups (monitor multiple channels as one)
- Advanced filtering (by keywords, authors, etc.)
- Monitoring presets (quick setup for common scenarios)

### Phase 3 Features (Scale)
- Real-time monitoring status updates (WebSocket)
- Predictive scheduling (ML-based optimal fetch times)
- Cross-platform monitoring (monitor related channels together)
- Monitoring recommendations (suggest channels to monitor)
- Advanced analytics and reporting

---

## 📚 Dependencies

### Internal Dependencies
- **Accounts App:** User model, authentication
- **Integrations App:** Channel model, platform connections

### External Dependencies
- **Django:** Web framework
- **Django REST Framework:** API framework
- **Celery:** Background task processing
- **Redis:** Message broker and cache
- **croniter:** Cron expression parsing
- **pytz:** Timezone handling

---

## 🎓 Acceptance Criteria

### User Acceptance
- [ ] Users can easily add channels to monitoring
- [ ] Users can configure fetch frequency
- [ ] Users can view monitoring status at a glance
- [ ] Users can troubleshoot monitoring issues
- [ ] Users receive timely notifications for issues

### Technical Acceptance
- [ ] All functional requirements met
- [ ] All non-functional requirements met
- [ ] 85%+ test coverage achieved
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Documentation complete and accurate

### Business Acceptance
- [ ] Monitoring reduces manual effort
- [ ] System scales to support growth
- [ ] Monitoring is reliable and accurate
- [ ] Users are satisfied with functionality
- [ ] System integrates seamlessly with other apps

---

# Made with Bob

Built with ❤️ by Bob, your AI coding assistant.