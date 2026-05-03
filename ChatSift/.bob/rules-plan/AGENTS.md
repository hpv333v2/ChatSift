# Plan Mode Rules (Non-Obvious Only)

## Architectural Constraints
- Backend must be Django-based (already scaffolded with Django 6.0.4)
- Frontend framework not yet chosen (empty directory exists)
- Database is SQLite by default (may need PostgreSQL for production per README)

## Hidden Coupling Between Components
*To be documented as component interactions are established*

## Non-Standard Patterns That Must Be Followed
- All Django commands execute from `backend/` subdirectory, not project root
- Project has name mismatch: "ChatSift" (README) vs "Infobyte" (Django project name)

## Performance Bottlenecks
*To be documented as performance patterns are discovered*

## Planned Integrations (from README)
- Discord API integration (not yet implemented)
- Telegram Bot API integration (not yet implemented)
- Task scheduling via Celery or Cron (not yet configured)
- LLM-based summarization (no AI integration yet)