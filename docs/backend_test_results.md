# ChatSift Backend Test Results

**Date:** 2026-05-03
**Backend:** Django dev server at http://localhost:8000 (venv at `Chatsift/ChatSift/backend/venv`)
**Test user:** sift1@example.com / TestPass123!

## Endpoint results

| # | Endpoint | Method | Auth | HTTP | Result |
|---|---|---|---|---|---|
| 1 | `/` | GET | — | 404 | Expected (no root view) |
| 2 | `/api/v1/auth/register/` | POST | — | 201 | PASS — returns user + access + refresh |
| 3 | `/api/v1/auth/login/` | POST | — | 200 | PASS — returns user + tokens |
| 4 | `/api/v1/auth/login/` (wrong pw) | POST | — | 400 | PASS — `Invalid email or password` |
| 5 | `/api/v1/users/me/` | GET | Bearer | 200 | PASS — returns user profile |
| 6 | `/api/v1/users/me/` (no token) | GET | — | 401 | PASS — `Authentication credentials were not provided` |
| 7 | `/api/v1/auth/email/status/` | GET | Bearer | 200 | PASS — `email_verified: false`, `can_create_integrations: false` |
| 8 | `/api/v1/auth/refresh/` | POST | — | 200 | PASS — rotates both access + refresh |
| 9 | `/api/v1/auth/email/verify/send/` | POST | Bearer | **500** | **FAIL — email service not configured** |
| 10 | `/api/v1/integrations/` | GET | Bearer | 200 | PASS — returns `{connections: []}` |
| 11 | `/api/v1/auth/logout/` (with rotated refresh) | POST | Bearer | 400 | Refresh already rotated; need to use the latest refresh from `/auth/refresh/` |
| 12 | `/api/v1/auth/refresh/` (after rotation) | POST | — | 401 | PASS — `Token is blacklisted` (rotation blacklisting works) |

## Important findings

- **URL is `/api/v1/users/me/`** (NOT `/api/v1/auth/me/`). Update any frontend or docs that reference `/auth/me/`.
- **Token rotation is enabled** — every `/auth/refresh/` call returns a new refresh AND blacklists the old one. Clients must always store the latest refresh.
- **Email sending is broken (500)** — `auth/email/verify/send/` returns `Failed to send verification email`. Likely missing SMTP config or `EMAIL_BACKEND` not set to console. Action: in `backend/Infobyte/settings.py`, set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` for local testing so the verification link prints to the terminal.
- **Integration creation is gated** by `can_create_integrations: false` until email is verified. So fixing email backend unblocks the Discord/Telegram OAuth path for the demo.

## Available URL patterns (from Django 404 page)

```
admin/
api/v1/auth/register/
api/v1/auth/login/
api/v1/auth/logout/
api/v1/auth/refresh/
api/v1/auth/email/verify/send/
api/v1/auth/email/verify/confirm/
api/v1/auth/email/status/
api/v1/users/me/
api/v1/integrations/
```

## Quick repro (Git Bash, Windows)

```bash
cd "c:/Users/harip/D/Coding_projects/IBM_BOB_Devday_Hackathon/Chatsift/ChatSift/backend"
./venv/Scripts/python.exe manage.py runserver 8000

# In another shell:
curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@x.com","username":"demo","password":"TestPass123!","password_confirm":"TestPass123!"}'

curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@x.com","password":"TestPass123!"}'
```

## Next actions for demo readiness

1. **Fix email backend** (5 min): set console email backend in `settings.py` so verification email prints to terminal. This unblocks the integrations path.
2. **Verify frontend client** uses `/api/v1/users/me/` (not `/auth/me/`).
3. **Run end-to-end frontend test** once email backend is fixed.
