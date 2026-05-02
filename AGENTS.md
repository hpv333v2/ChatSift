# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Context (Non-Obvious)
- **Name Mismatch**: README refers to "ChatSift" but Django project is named "Infobyte"
- **Django Version**: Uses Django 6.0.4 (recent 6.0.x series)
- **Missing Dependencies**: No requirements.txt/pyproject.toml exists despite Django REST Framework being in INSTALLED_APPS
- **Empty Frontend**: `frontend/` directory exists but contains no files yet

## Commands (Non-Standard Locations)
All Django commands MUST be run from `backend/` directory, not project root:
```bash
cd backend && python manage.py runserver
cd backend && python manage.py migrate
cd backend && python manage.py createsuperuser
cd backend && python manage.py test
```

## Code Style & Conventions
*To be documented as patterns emerge*

## Architecture Notes
- Backend: Django 6.0.4 + Django REST Framework
- Database: SQLite (default, see backend/Infobyte/settings.py line 77-82)
- Frontend: Not yet implemented
- Task Scheduling: Planned (Celery/Cron - see README)
- Integrations: Discord API, Telegram Bot API (planned)

## Security Notes
- Development secret key is hardcoded in backend/Infobyte/settings.py (line 23)
- DEBUG=True in settings (line 26)
- ALLOWED_HOSTS=[] (line 28)

## Testing
*No test framework configured yet*

## Custom Utilities
*To be documented as they are created*