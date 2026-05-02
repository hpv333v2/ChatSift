# 🤖 Summaries API - Implementation Plan

## 📋 Overview
This document outlines the comprehensive implementation plan for the ChatSift summaries app, which handles AI-powered summarization of chat messages using LLM integration. The summaries app is the core intelligence layer that transforms raw message data into actionable insights.

## 🎯 Purpose & Scope

### What This App Does
- Generates AI-powered summaries from message batches
- Manages summary sections (key points, decisions, action items, trends, highlights)
- Integrates with multiple LLM providers (OpenAI, Anthropic, local models)
- Tracks LLM usage and costs
- Provides summary retrieval and management APIs

### Dependencies
- **Upstream:** [`messages`](../messages/) app (MessageBatch, Message models)
- **Upstream:** [`monitoring`](../monitoring/) app (MonitoredChannel model)
- **Downstream:** [`notifications`](../notifications/) app (consumes summaries for delivery)

## 📊 Current State Analysis

### Existing Setup
- ✅ Django 6.0.4 installed
- ✅ Django REST Framework 3.17.1 installed
- ✅ Celery 5.3.6 configured for async tasks
- ✅ Redis 5.0.1 for Celery broker
- ✅ `summaries` app created (empty)
- ❌ No models defined yet
- ❌ No LLM integration configured
- ❌ No API endpoints implemented

### Required Dependencies
```txt
# LLM Providers
openai==1.12.0                    # OpenAI GPT models
anthropic==0.18.1                 # Anthropic Claude models
langchain==0.1.9                  # LLM orchestration (optional)
tiktoken==0.6.0                   # Token counting for OpenAI

# Additional utilities
python-dateutil==2.8.2            # Date parsing
```

## 🗂️ App Structure

### Directory Layout
```
backend/summaries/
├── __init__.py
├── admin.py                      # Django admin configuration
├── apps.py                       # App configuration
├── models.py                     # Summary and SummarySection models
├── serializers.py                # DRF serializers
├── views.py                      # API views
├── urls.py                       # URL routing
├── permissions.py                # Custom permissions
├── tasks.py                      # Celery tasks for summary generation
├── signals.py                    # Django signals
├── services/
│   ├── __init__.py
│   ├── base_llm_service.py      # Base LLM service class
│   ├── openai_service.py        # OpenAI integration
│   ├── anthropic_service.py     # Anthropic integration
│   ├── local_llm_service.py     # Local LLM integration
│   ├── preprocessor.py          # Message preprocessing
│   ├── context_builder.py       # Context building for LLM
│   └── response_parser.py       # Parse LLM responses
├── prompts/
│   ├── __init__.py
│   ├── summary_prompts.py       # Prompt templates
│   └── prompt_builder.py        # Dynamic prompt construction
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   ├── test_tasks.py
│   ├── test_services.py
│   └── test_permissions.py
├── docs/
│   ├── SUMMARIES_API_IMPLEMENTATION_PLAN.md  # This file
│   ├── SUMMARIES_API_REQUIREMENTS.md
│   ├── SUMMARIES_API_FLOW.md
│   └── LLM_INTEGRATION_GUIDE.md
└── migrations/
    └── __init__.py
```

## 🗄️ Database Models

### 1. Summary Model
**File:** [`summaries/models.py`](../models.py)

```python
class Summary(models.Model):
    """
    Represents an AI-generated summary of messages from a monitored channel.
    Links to a message batch and contains multiple summary sections.
    """
    
    GENERATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    monitored_channel = models.ForeignKey(
        'monitoring.MonitoredChannel',
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    batch = models.ForeignKey(
        'messages.MessageBatch',
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    
    # Summary period
    summary_date = models.DateField(help_text='Date this summary covers')
    summary_period_start = models.DateTimeField()
    summary_period_end = models.DateTimeField()
    
    # Statistics
    total_messages = models.IntegerField(default=0)
    active_participants = models.IntegerField(default=0)
    
    # Generation tracking
    generation_status = models.CharField(
        max_length=20,
        choices=GENERATION_STATUS_CHOICES,
        default='PENDING'
    )
    llm_model = models.CharField(
        max_length=100,
        help_text='LLM model used (e.g., gpt-4, claude-3-opus)'
    )
    llm_tokens_used = models.IntegerField(null=True, blank=True)
    llm_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Estimated cost in USD'
    )
    generation_time_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'summaries'
        ordering = ['-summary_date', '-created_at']
        indexes = [
            models.Index(fields=['monitored_channel', 'summary_date']),
            models.Index(fields=['generation_status']),
            models.Index(fields=['summary_date']),
        ]
        unique_together = [['monitored_channel', 'summary_date']]
```

### 2. SummarySection Model
**File:** [`summaries/models.py`](../models.py)

```python
class SummarySection(models.Model):
    """
    Represents a section within a summary (e.g., key points, decisions).
    Each summary has multiple sections organized by type and order.
    """
    
    SECTION_TYPE_CHOICES = [
        ('KEY_POINTS', 'Key Points'),
        ('DECISIONS', 'Decisions Made'),
        ('ACTION_ITEMS', 'Action Items'),
        ('TRENDS', 'Notable Trends'),
        ('HIGHLIGHTS', 'Highlights'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES
    )
    section_order = models.IntegerField(
        help_text='Display order within the summary'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text='AI confidence score (0.0-1.0)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'summary_sections'
        ordering = ['summary', 'section_order']
        indexes = [
            models.Index(fields=['summary', 'section_order']),
            models.Index(fields=['section_type']),
        ]
```

## 🔌 API Endpoints

### Summary Management Endpoints

#### 1. List Summaries
```
GET /api/summaries/
```
**Purpose:** List all summaries for the authenticated user's monitored channels

**Query Parameters:**
- `monitored_channel` (UUID, optional) - Filter by monitored channel
- `date_from` (date, optional) - Filter summaries from this date
- `date_to` (date, optional) - Filter summaries to this date
- `status` (string, optional) - Filter by generation status
- `page` (int, optional) - Page number for pagination
- `page_size` (int, optional) - Items per page

**Response:**
```json
{
  "count": 25,
  "next": "http://api.example.com/api/summaries/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "monitored_channel": {
        "id": "uuid",
        "channel_name": "general",
        "platform": "discord"
      },
      "summary_date": "2026-05-02",
      "summary_period_start": "2026-05-02T00:00:00Z",
      "summary_period_end": "2026-05-02T23:59:59Z",
      "total_messages": 156,
      "active_participants": 12,
      "generation_status": "COMPLETED",
      "llm_model": "gpt-4-turbo",
      "sections_count": 5,
      "created_at": "2026-05-03T01:00:00Z"
    }
  ]
}
```

#### 2. Retrieve Summary Detail
```
GET /api/summaries/{id}/
```
**Purpose:** Get detailed summary with all sections

**Response:**
```json
{
  "id": "uuid",
  "monitored_channel": {
    "id": "uuid",
    "channel_name": "general",
    "platform": "discord"
  },
  "batch": {
    "id": "uuid",
    "message_count": 156
  },
  "summary_date": "2026-05-02",
  "summary_period_start": "2026-05-02T00:00:00Z",
  "summary_period_end": "2026-05-02T23:59:59Z",
  "total_messages": 156,
  "active_participants": 12,
  "generation_status": "COMPLETED",
  "llm_model": "gpt-4-turbo",
  "llm_tokens_used": 3500,
  "llm_cost": "0.0525",
  "generation_time_seconds": 4.2,
  "sections": [
    {
      "id": "uuid",
      "section_type": "KEY_POINTS",
      "section_order": 1,
      "title": "Key Discussion Points",
      "content": "1. Team discussed new feature requirements...",
      "confidence_score": 0.92
    },
    {
      "id": "uuid",
      "section_type": "DECISIONS",
      "section_order": 2,
      "title": "Decisions Made",
      "content": "1. Approved migration to new database...",
      "confidence_score": 0.88
    }
  ],
  "created_at": "2026-05-03T01:00:00Z",
  "updated_at": "2026-05-03T01:00:15Z"
}
```

#### 3. Generate Summary (Manual Trigger)
```
POST /api/summaries/generate/
```
**Purpose:** Manually trigger summary generation for a monitored channel

**Request Body:**
```json
{
  "monitored_channel_id": "uuid",
  "date": "2026-05-02",
  "llm_provider": "openai"  // optional: openai, anthropic, local
}
```

**Response:**
```json
{
  "id": "uuid",
  "monitored_channel_id": "uuid",
  "generation_status": "PENDING",
  "task_id": "celery-task-uuid",
  "message": "Summary generation started"
}
```

#### 4. Regenerate Summary
```
POST /api/summaries/{id}/regenerate/
```
**Purpose:** Regenerate an existing summary (useful if generation failed)

**Request Body:**
```json
{
  "llm_provider": "anthropic"  // optional: switch provider
}
```

#### 5. Delete Summary
```
DELETE /api/summaries/{id}/
```
**Purpose:** Delete a summary and all its sections

#### 6. Summary Statistics
```
GET /api/summaries/statistics/
```
**Purpose:** Get summary generation statistics for the user

**Query Parameters:**
- `date_from` (date, optional)
- `date_to` (date, optional)

**Response:**
```json
{
  "total_summaries": 45,
  "completed_summaries": 42,
  "failed_summaries": 3,
  "total_messages_summarized": 6780,
  "total_tokens_used": 145000,
  "total_cost": "21.75",
  "average_generation_time": 3.8,
  "summaries_by_status": {
    "COMPLETED": 42,
    "FAILED": 3
  },
  "summaries_by_provider": {
    "openai": 30,
    "anthropic": 12
  }
}
```

## 🔐 Permissions

### Custom Permissions
**File:** [`summaries/permissions.py`](../permissions.py)

```python
class IsSummaryOwner(BasePermission):
    """
    Permission to check if user owns the summary
    (via monitored_channel ownership)
    """
    
class CanGenerateSummary(BasePermission):
    """
    Permission to check if user can generate summaries
    (email verified, has active monitored channels)
    """
```

## 🤖 LLM Integration Architecture

### Service Layer Structure

#### 1. Base LLM Service
**File:** [`summaries/services/base_llm_service.py`](../services/base_llm_service.py)

```python
class BaseLLMService(ABC):
    """Abstract base class for LLM integrations"""
    
    @abstractmethod
    def generate_summary(self, messages, context):
        """Generate summary from messages"""
        pass
    
    @abstractmethod
    def count_tokens(self, text):
        """Count tokens in text"""
        pass
    
    @abstractmethod
    def calculate_cost(self, tokens):
        """Calculate cost for token usage"""
        pass
```

#### 2. OpenAI Service
**File:** [`summaries/services/openai_service.py`](../services/openai_service.py)

- Integrates with OpenAI GPT-4/GPT-3.5
- Handles token counting with tiktoken
- Implements retry logic with exponential backoff
- Tracks costs based on model pricing

#### 3. Anthropic Service
**File:** [`summaries/services/anthropic_service.py`](../services/anthropic_service.py)

- Integrates with Claude 3 (Opus, Sonnet, Haiku)
- Handles Anthropic-specific API format
- Implements streaming responses (optional)

#### 4. Preprocessor
**File:** [`summaries/services/preprocessor.py`](../services/preprocessor.py)

**Functions:**
- Remove bot messages and system notifications
- Filter spam and irrelevant content
- Deduplicate similar messages
- Extract URLs, mentions, hashtags
- Identify conversation threads
- Normalize message format

#### 5. Context Builder
**File:** [`summaries/services/context_builder.py`](../services/context_builder.py)

**Functions:**
- Group messages by topic/thread
- Identify key participants
- Extract temporal patterns
- Build conversation context
- Prepare structured prompt data

#### 6. Response Parser
**File:** [`summaries/services/response_parser.py`](../services/response_parser.py)

**Functions:**
- Parse LLM JSON response
- Validate response structure
- Extract confidence scores
- Create SummarySection objects
- Handle parsing errors gracefully

## 📝 Prompt Templates

### Summary Generation Prompt
**File:** [`summaries/prompts/summary_prompts.py`](../prompts/summary_prompts.py)

```python
SUMMARY_PROMPT_TEMPLATE = """
You are an AI assistant that summarizes group chat conversations.

Context:
- Channel: {channel_name} ({platform})
- Date: {date}
- Total Messages: {message_count}
- Active Participants: {participant_count}
- Time Period: {period_start} to {period_end}

Messages:
{formatted_messages}

Generate a structured summary with the following sections:

1. KEY_POINTS: 3-5 main topics or themes discussed
2. DECISIONS: Any decisions made or consensus reached
3. ACTION_ITEMS: Tasks, follow-ups, or action items mentioned
4. TRENDS: Patterns, recurring themes, or notable trends
5. HIGHLIGHTS: Interesting, important, or noteworthy moments

For each section:
- Provide a clear title
- Write concise, bullet-point content
- Include a confidence score (0.0-1.0) indicating how certain you are

Format your response as JSON:
{{
  "sections": [
    {{
      "section_type": "KEY_POINTS",
      "title": "Main Discussion Topics",
      "content": "• Topic 1\\n• Topic 2\\n• Topic 3",
      "confidence_score": 0.95
    }},
    ...
  ]
}}

Focus on actionable insights and meaningful information. Ignore spam, off-topic chatter, and bot messages.
"""
```

## ⚙️ Celery Tasks

### Summary Generation Task
**File:** [`summaries/tasks.py`](../tasks.py)

```python
@shared_task(bind=True, max_retries=3)
def generate_summary_task(self, monitored_channel_id, date, llm_provider='openai'):
    """
    Celery task to generate summary for a monitored channel
    
    Args:
        monitored_channel_id: UUID of monitored channel
        date: Date to generate summary for (YYYY-MM-DD)
        llm_provider: LLM provider to use (openai, anthropic, local)
    """
    pass

@shared_task
def generate_daily_summaries():
    """
    Scheduled task to generate summaries for all active monitored channels
    Runs daily at configured time
    """
    pass

@shared_task
def retry_failed_summaries():
    """
    Retry generation for summaries that failed
    Runs every 6 hours
    """
    pass
```

## 🧪 Testing Strategy

### Test Coverage Areas

1. **Model Tests** ([`tests/test_models.py`](../tests/test_models.py))
   - Summary model creation and validation
   - SummarySection relationships
   - Model properties and methods
   - Database constraints

2. **Serializer Tests** ([`tests/test_serializers.py`](../tests/test_serializers.py))
   - Serialization/deserialization
   - Validation rules
   - Nested serializers
   - Read-only fields

3. **View Tests** ([`tests/test_views.py`](../tests/test_views.py))
   - API endpoint responses
   - Authentication/authorization
   - Query parameter filtering
   - Pagination

4. **Service Tests** ([`tests/test_services.py`](../tests/test_services.py))
   - LLM service integrations (mocked)
   - Preprocessor logic
   - Context builder
   - Response parser

5. **Task Tests** ([`tests/test_tasks.py`](../tests/test_tasks.py))
   - Celery task execution
   - Retry logic
   - Error handling

## 🚀 Implementation Phases

### Phase 1: Foundation (Priority: Critical)
**Estimated Time:** 4-5 hours

- [ ] Create database models (Summary, SummarySection)
- [ ] Run migrations
- [ ] Set up admin interface
- [ ] Write model unit tests

### Phase 2: LLM Services (Priority: Critical)
**Estimated Time:** 6-8 hours

- [ ] Implement base LLM service
- [ ] Create OpenAI service integration
- [ ] Create Anthropic service integration
- [ ] Implement preprocessor
- [ ] Implement context builder
- [ ] Implement response parser
- [ ] Write service tests (with mocks)

### Phase 3: API Layer (Priority: High)
**Estimated Time:** 4-5 hours

- [ ] Create serializers
- [ ] Implement permissions
- [ ] Create API views
- [ ] Set up URL routing
- [ ] Write API tests

### Phase 4: Celery Tasks (Priority: High)
**Estimated Time:** 3-4 hours

- [ ] Implement summary generation task
- [ ] Implement scheduled tasks
- [ ] Configure Celery beat schedule
- [ ] Write task tests

### Phase 5: Prompt Engineering (Priority: Medium)
**Estimated Time:** 2-3 hours

- [ ] Create prompt templates
- [ ] Implement prompt builder
- [ ] Test and refine prompts
- [ ] Document prompt strategies

### Phase 6: Integration & Testing (Priority: High)
**Estimated Time:** 3-4 hours

- [ ] Integration testing with messages app
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Error handling refinement

## 📋 Environment Configuration

### Required Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.3

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.3

# Local LLM Configuration (optional)
LOCAL_LLM_ENDPOINT=http://localhost:8000
LOCAL_LLM_MODEL=llama-2-70b

# Summary Configuration
DEFAULT_LLM_PROVIDER=openai
SUMMARY_GENERATION_TIMEOUT=300  # seconds
MAX_MESSAGES_PER_SUMMARY=1000
```

## 🔄 Integration Points

### Upstream Dependencies
1. **messages.MessageBatch** - Source of messages to summarize
2. **messages.Message** - Individual messages
3. **monitoring.MonitoredChannel** - Channel configuration

### Downstream Consumers
1. **notifications** app - Delivers summaries to users
2. **Dashboard** - Displays summary statistics

## 📊 Success Metrics

- Summary generation success rate > 95%
- Average generation time < 10 seconds
- Token usage optimization (< 5000 tokens per summary)
- User satisfaction with summary quality
- Cost per summary < $0.10

## 🚨 Error Handling

### Common Failure Scenarios
1. **LLM API Timeout** - Retry with exponential backoff
2. **Invalid API Key** - Log error, notify admin
3. **Token Limit Exceeded** - Truncate messages, retry
4. **Parsing Error** - Fallback to simpler prompt
5. **No Messages** - Skip summary generation

## 📚 Additional Documentation

- [`SUMMARIES_API_REQUIREMENTS.md`](./SUMMARIES_API_REQUIREMENTS.md) - Detailed requirements
- [`SUMMARIES_API_FLOW.md`](./SUMMARIES_API_FLOW.md) - Flow diagrams
- [`LLM_INTEGRATION_GUIDE.md`](./LLM_INTEGRATION_GUIDE.md) - LLM integration details

---

**Total Estimated Implementation Time:** 22-29 hours

**Priority Order:**
1. Phase 1: Foundation (models)
2. Phase 2: LLM Services (core functionality)
3. Phase 3: API Layer (user interface)
4. Phase 4: Celery Tasks (automation)
5. Phase 5: Prompt Engineering (optimization)
6. Phase 6: Integration & Testing (quality assurance)