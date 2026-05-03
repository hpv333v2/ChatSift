# Advanced Mode Rules (Non-Obvious Only)

## Project-Specific Patterns
*To be documented as custom utilities and patterns are created*

## Non-Standard Approaches
- Django commands must be run from `backend/` directory, not project root
- Virtual environment location: `/home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate`
- All Python/Django/pip commands MUST be prefixed with: `source /home/krazy/Hackathons/virtualenvs/ibmhackathon/bin/activate && `
- If virtual environment doesn't exist at that path, prompt user to create one and update this file with new path

## Critical Gotchas
- Django REST Framework is in INSTALLED_APPS but not in any dependency file
- Project name mismatch: README says "ChatSift", Django project is "Infobyte"
- Frontend directory exists but is empty - no framework chosen yet

## MCP & Browser Tool Usage
*To be documented as MCP servers and browser automation patterns are established*

## Import Conventions
*To be documented as code patterns emerge*

## Error Handling Patterns
*To be documented as error handling patterns are established*