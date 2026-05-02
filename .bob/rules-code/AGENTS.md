# Code Mode Rules (Non-Obvious Only)

## Project-Specific Patterns
*To be documented as custom utilities and patterns are created*

## Non-Standard Approaches
- Django commands must be run from `backend/` directory, not project root
- No dependency management file exists yet (requirements.txt/pyproject.toml missing)

## Critical Gotchas
- Django REST Framework is in INSTALLED_APPS but not in any dependency file
- Project name mismatch: README says "ChatSift", Django project is "Infobyte"
- Frontend directory exists but is empty - no framework chosen yet

## Import Conventions
*To be documented as code patterns emerge*

## Error Handling Patterns
*To be documented as error handling patterns are established*