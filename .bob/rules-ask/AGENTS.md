# Ask Mode Rules (Non-Obvious Only)

## Documentation Context
- Project README refers to "ChatSift" but actual Django project is named "Infobyte"
- Frontend directory exists but is completely empty (no framework chosen)
- No dependency files exist despite Django REST Framework being configured

## Hidden or Misnamed Documentation
*To be documented as documentation patterns emerge*

## Counterintuitive Code Organization
- All Django management commands must be run from `backend/` subdirectory
- Project root contains empty `frontend/` directory with no indication of planned framework

## Important Context Not Evident from File Structure
- Django 6.0.4 is used (very recent version, may have breaking changes from older tutorials)
- SQLite is configured as database (see backend/Infobyte/settings.py)
- Development secret key is hardcoded and exposed
- No test framework or CI/CD configured yet