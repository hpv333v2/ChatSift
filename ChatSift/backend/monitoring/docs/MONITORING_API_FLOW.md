# 🔄 Monitoring API - Flow Diagrams

## 📊 System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        U[User]
    end
    
    subgraph "API Layer"
        API[Monitoring API]
        AUTH[Authentication]
        PERM[Permissions]
    end
    
    subgraph "Business Logic"
        MON[Monitoring Service]
        SCHED[Schedule Manager]
        STATS[Statistics Service]
    end
    
    subgraph "Data Layer"
        MC[MonitoredChannel Model]
        MS[MonitoringSchedule Model]
        CH[Channel Model - Integrations]
    end
    
    subgraph "Background Tasks"
        SYNC[Sync Schedules Task]
        CHECK[Check Due Schedules Task]
        HEALTH[Health Check Task]
        CLEANUP[Cleanup Task]
    end
    
    subgraph "External Apps"
        INT[Integrations App]
        MSG[Messages App]
        SUM[Summaries App]
    end
    
    U --> API
    API --> AUTH
    AUTH --> PERM
    PERM --> MON
    MON --> MC
    MON --> SCHED
    SCHED --> MS
    MC --> CH
    
    MON --> SYNC
    SCHED --> CHECK
    CHECK --> MSG
    CHECK --> SUM
    
    HEALTH --> MC
    CLEANUP --> MC
    
    MC -.-> INT
    STATS --> MC
    STATS --> MS
```

---

## 🎯 Core Workflows

### 1. Add Channel to Monitoring Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as Monitoring API
    participant AUTH as Auth/Permissions
    participant MON as Monitoring Service
    participant DB as Database
    participant SCHED as Schedule Manager
    participant CELERY as Celery

    U->>API: POST /api/monitoring/channels/
    API->>AUTH: Verify authentication
    AUTH->>AUTH: Check email verified
    AUTH->>AUTH: Check has active connection
    AUTH-->>API: Authorized
    
    API->>MON: Create monitored channel
    MON->>DB: Check channel not already monitored
    DB-->>MON: Validation passed
    
    MON->>DB: Create MonitoredChannel
    DB-->>MON: Channel created
    
    MON->>SCHED: Sync schedules
    SCHED->>DB: Create FETCH schedule
    SCHED->>DB: Create SUMMARIZE schedule
    SCHED->>SCHED: Calculate next run times
    DB-->>SCHED: Schedules created
    
    SCHED->>CELERY: Queue sync task
    CELERY-->>SCHED: Task queued
    
    MON-->>API: Success response
    API-->>U: 201 Created with monitoring details
```

---

### 2. Update Fetch Frequency Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as Monitoring API
    participant AUTH as Auth/Permissions
    participant MON as Monitoring Service
    participant DB as Database
    participant SCHED as Schedule Manager

    U->>API: PATCH /api/monitoring/channels/{id}/
    API->>AUTH: Verify ownership
    AUTH-->>API: Authorized
    
    API->>MON: Update frequency
    MON->>DB: Get MonitoredChannel
    DB-->>MON: Channel data
    
    MON->>DB: Update fetch_frequency
    DB-->>MON: Updated
    
    MON->>SCHED: Recalculate schedules
    SCHED->>DB: Get FETCH schedule
    SCHED->>SCHED: Convert frequency to cron
    SCHED->>SCHED: Calculate next run time
    SCHED->>DB: Update schedule
    DB-->>SCHED: Schedule updated
    
    MON-->>API: Success response
    API-->>U: 200 OK with updated config
```

---

### 3. Schedule Execution Flow

```mermaid
sequenceDiagram
    participant BEAT as Celery Beat
    participant CHECK as Check Due Schedules Task
    participant DB as Database
    participant FETCH as Fetch Messages Task
    participant SUMM as Summarize Task
    participant MON as Monitoring Service

    BEAT->>CHECK: Run every 5 minutes
    CHECK->>DB: Query due schedules
    DB-->>CHECK: List of due schedules
    
    loop For each due schedule
        CHECK->>CHECK: Check schedule type
        
        alt Schedule type is FETCH
            CHECK->>FETCH: Trigger fetch task
            FETCH->>FETCH: Fetch messages from platform
            FETCH->>DB: Update message_count
            FETCH->>DB: Update last_fetched_at
        else Schedule type is SUMMARIZE
            CHECK->>SUMM: Trigger summarize task
            SUMM->>SUMM: Generate summary
        end
        
        CHECK->>DB: Update last_run_at
        CHECK->>DB: Calculate next_run_at
        CHECK->>DB: Increment run_count
    end
    
    CHECK->>MON: Update monitoring status
    MON-->>CHECK: Status updated
```

---

### 4. Health Check Flow

```mermaid
sequenceDiagram
    participant BEAT as Celery Beat
    participant HEALTH as Health Check Task
    participant DB as Database
    participant ALERT as Alert Service
    participant MON as Monitoring Service

    BEAT->>HEALTH: Run every 6 hours
    HEALTH->>DB: Get all active monitored channels
    DB-->>HEALTH: List of channels
    
    loop For each channel
        HEALTH->>HEALTH: Calculate expected interval
        HEALTH->>HEALTH: Check last_fetched_at
        
        alt Fetch is stale (> 2x frequency)
            HEALTH->>DB: Mark as stale
            HEALTH->>ALERT: Send stale alert
            HEALTH->>HEALTH: Calculate health score (low)
        else Fetch is recent
            HEALTH->>HEALTH: Calculate health score (high)
        end
        
        HEALTH->>DB: Update health status
    end
    
    HEALTH->>MON: Generate health report
    MON-->>HEALTH: Report generated
```

---

## 🔄 State Transitions

### MonitoredChannel States

```mermaid
stateDiagram-v2
    [*] --> Active: Create monitoring
    Active --> Paused: User pauses
    Paused --> Active: User resumes
    Active --> Stale: No fetch in 2x frequency
    Stale --> Active: Successful fetch
    Active --> Ended: monitoring_end_date reached
    Paused --> Ended: monitoring_end_date reached
    Ended --> [*]: Cleanup after 30 days
    
    note right of Active
        is_active = True
        Schedules active
        Fetching messages
    end note
    
    note right of Paused
        is_active = False
        Schedules inactive
        No fetching
    end note
    
    note right of Stale
        is_active = True
        Schedules active
        But fetching failing
    end note
    
    note right of Ended
        monitoring_end_date passed
        Schedules inactive
        Archived
    end note
```

---

### MonitoringSchedule States

```mermaid
stateDiagram-v2
    [*] --> Pending: Create schedule
    Pending --> Due: next_run_at <= now
    Due --> Running: Task started
    Running --> Success: Task completed
    Running --> Failed: Task failed
    Success --> Pending: Calculate next run
    Failed --> Pending: Retry with backoff
    Pending --> Inactive: Monitoring paused
    Inactive --> Pending: Monitoring resumed
    
    note right of Pending
        Waiting for next run
        next_run_at in future
    end note
    
    note right of Due
        Ready to execute
        next_run_at <= now
    end note
    
    note right of Running
        Task in progress
        Being executed
    end note
```

---

## 📋 Data Flow Diagrams

### 1. Monitoring Creation Data Flow

```mermaid
graph LR
    A[User Input] --> B[Validation]
    B --> C{Valid?}
    C -->|No| D[Error Response]
    C -->|Yes| E[Create MonitoredChannel]
    E --> F[Create FETCH Schedule]
    E --> G[Create SUMMARIZE Schedule]
    F --> H[Calculate Next Run]
    G --> H
    H --> I[Queue Sync Task]
    I --> J[Success Response]
```

---

### 2. Schedule Execution Data Flow

```mermaid
graph TB
    A[Celery Beat Trigger] --> B[Query Due Schedules]
    B --> C{Schedules Found?}
    C -->|No| D[Wait 5 minutes]
    C -->|Yes| E[Process Each Schedule]
    E --> F{Schedule Type?}
    F -->|FETCH| G[Trigger Fetch Task]
    F -->|SUMMARIZE| H[Trigger Summarize Task]
    G --> I[Update Schedule]
    H --> I
    I --> J[Calculate Next Run]
    J --> K[Update Database]
    K --> D
```

---

### 3. Health Check Data Flow

```mermaid
graph TB
    A[Health Check Trigger] --> B[Get Active Channels]
    B --> C[For Each Channel]
    C --> D{Last Fetch Recent?}
    D -->|Yes| E[Calculate High Health Score]
    D -->|No| F[Mark as Stale]
    F --> G[Calculate Low Health Score]
    E --> H[Update Status]
    G --> H
    H --> I{More Channels?}
    I -->|Yes| C
    I -->|No| J[Generate Report]
    J --> K[Send Alerts if Needed]
```

---

## 🔗 Integration Points

### With Integrations App

```mermaid
graph LR
    subgraph "Integrations App"
        PC[PlatformConnection]
        CH[Channel]
    end
    
    subgraph "Monitoring App"
        MC[MonitoredChannel]
        MS[MonitoringSchedule]
    end
    
    PC -->|has many| CH
    CH -->|monitored by| MC
    MC -->|has many| MS
    
    MC -.->|validates| PC
    MC -.->|references| CH
```

**Integration Flow:**
1. User connects platform (Integrations App)
2. Channels are discovered and stored (Integrations App)
3. User selects channels to monitor (Monitoring App)
4. Monitoring validates channel belongs to user's connection
5. Monitoring creates schedules for selected channels

---

### With Messages App (Future)

```mermaid
sequenceDiagram
    participant SCHED as Schedule Checker
    participant MC as MonitoredChannel
    participant FETCH as Fetch Task
    participant MSG as Messages App
    participant DB as Database

    SCHED->>MC: Get due FETCH schedules
    MC-->>SCHED: List of channels to fetch
    
    loop For each channel
        SCHED->>FETCH: Trigger fetch task
        FETCH->>MSG: Request message fetch
        MSG->>MSG: Fetch from platform API
        MSG->>DB: Store messages
        MSG-->>FETCH: Fetch complete (count)
        FETCH->>MC: Update message_count
        FETCH->>MC: Update last_fetched_at
    end
```

---

### With Summaries App (Future)

```mermaid
sequenceDiagram
    participant SCHED as Schedule Checker
    participant MC as MonitoredChannel
    participant SUMM as Summarize Task
    participant SUM as Summaries App
    participant MSG as Messages App
    participant DB as Database

    SCHED->>MC: Get due SUMMARIZE schedules
    MC-->>SCHED: List of channels to summarize
    
    loop For each channel
        SCHED->>SUMM: Trigger summarize task
        SUMM->>MSG: Get messages for period
        MSG-->>SUMM: Message batch
        SUMM->>SUM: Request summary generation
        SUM->>SUM: Generate AI summary
        SUM->>DB: Store summary
        SUM-->>SUMM: Summary complete
    end
```

---

## 🎯 User Journey Flows

### Journey 1: First-Time Setup

```mermaid
graph TD
    A[User logs in] --> B[Connects Discord/Telegram]
    B --> C[Views available channels]
    C --> D[Selects channels to monitor]
    D --> E[Chooses fetch frequency]
    E --> F[Confirms monitoring setup]
    F --> G[System creates schedules]
    G --> H[User views monitoring dashboard]
    H --> I[Waits for first fetch]
    I --> J[Views fetched messages]
    J --> K[Receives first summary]
```

---

### Journey 2: Managing Monitoring

```mermaid
graph TD
    A[User views monitored channels] --> B{Action?}
    B -->|Change frequency| C[Update frequency]
    B -->|Pause monitoring| D[Deactivate channel]
    B -->|Resume monitoring| E[Reactivate channel]
    B -->|Stop monitoring| F[Delete monitoring]
    B -->|View stats| G[Check statistics]
    
    C --> H[System recalculates schedules]
    D --> I[System pauses schedules]
    E --> J[System resumes schedules]
    F --> K[System archives data]
    G --> L[View health & metrics]
    
    H --> M[Confirmation]
    I --> M
    J --> M
    K --> M
    L --> M
```

---

### Journey 3: Troubleshooting

```mermaid
graph TD
    A[User notices missing messages] --> B[Checks monitoring status]
    B --> C{Status?}
    C -->|Active| D[Check last fetch time]
    C -->|Stale| E[View error logs]
    C -->|Paused| F[Resume monitoring]
    
    D --> G{Recent fetch?}
    G -->|Yes| H[Check message filters]
    G -->|No| I[Manually trigger sync]
    
    E --> J[Identify error cause]
    J --> K{Fixable?}
    K -->|Yes| L[Fix configuration]
    K -->|No| M[Contact support]
    
    F --> N[Monitoring resumed]
    I --> N
    L --> N
```

---

## 🔄 Background Task Scheduling

### Celery Beat Schedule

```mermaid
gantt
    title Monitoring Background Tasks Schedule
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Every 5 Minutes
    Check Due Schedules :active, 00:00, 5m
    Check Due Schedules :active, 00:05, 5m
    Check Due Schedules :active, 00:10, 5m
    
    section Every 6 Hours
    Health Check :crit, 00:00, 30m
    Health Check :crit, 06:00, 30m
    Health Check :crit, 12:00, 30m
    Health Check :crit, 18:00, 30m
    
    section Weekly
    Cleanup Inactive :milestone, 00:00, 1h
```

---

## 📊 Performance Considerations

### Query Optimization Flow

```mermaid
graph TB
    A[API Request] --> B{Needs Related Data?}
    B -->|Yes| C[Use select_related]
    B -->|No| D[Simple query]
    
    C --> E{Multiple Relations?}
    E -->|Yes| F[Use prefetch_related]
    E -->|No| G[Continue with select_related]
    
    F --> H[Optimize query]
    G --> H
    D --> H
    
    H --> I{Large Dataset?}
    I -->|Yes| J[Add pagination]
    I -->|No| K[Return results]
    
    J --> L[Add filtering]
    L --> M[Add indexing]
    M --> K
```

---

## 🎓 Key Takeaways

### Critical Flows to Understand
1. **Monitoring Creation:** User → API → Validation → Database → Schedule Creation
2. **Schedule Execution:** Celery Beat → Check Due → Trigger Tasks → Update Status
3. **Health Monitoring:** Periodic Check → Detect Issues → Alert → Update Status
4. **Integration:** Monitoring ← Integrations → Messages → Summaries

### Important State Transitions
- Active ↔ Paused (user control)
- Active → Stale (system detection)
- Pending → Due → Running → Success/Failed (schedule lifecycle)

### Performance Patterns
- Use select_related for ForeignKey
- Use prefetch_related for reverse ForeignKey
- Add indexes on frequently queried fields
- Implement pagination for large datasets
- Cache statistics and computed values

---

# Made with Bob

Built with ❤️ by Bob, your AI coding assistant.