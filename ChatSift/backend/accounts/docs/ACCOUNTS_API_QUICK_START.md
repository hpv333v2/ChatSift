# 🚀 Account APIs - Quick Start Guide

## 📋 Summary

This guide provides a quick reference for implementing the ChatSift account APIs with the following specifications:

- **Authentication:** JWT with Authorization headers
- **Email Service:** SendGrid (100 free emails/day)
- **Email Verification:** Optional on signup, required for integrations
- **OAuth:** Not implemented (future feature)

## 🎯 Implementation Checklist

### Phase 1: Setup (Day 1)
- [ ] Install dependencies: `djangorestframework-simplejwt`, `sendgrid`, `django-cors-headers`, `python-decouple`
- [ ] Create accounts app: `python manage.py startapp accounts`
- [ ] Update [`settings.py`](backend/Infobyte/settings.py) with JWT, CORS, and SendGrid config
- [ ] Create `.env` file with environment variables

### Phase 2: Models (Day 1)
- [ ] Implement custom User model with `email_verified` field
- [ ] Implement UserProfile model
- [ ] Create custom user manager
- [ ] Add signal to auto-create UserProfile
- [ ] Run migrations

### Phase 3: Serializers & Validators (Day 2)
- [ ] UserRegistrationSerializer
- [ ] UserLoginSerializer
- [ ] UserProfileSerializer
- [ ] EmailVerificationSerializer
- [ ] PasswordResetSerializer
- [ ] Custom password validators

### Phase 4: Views & Permissions (Day 2-3)
- [ ] Registration view
- [ ] Login view
- [ ] Logout view (token blacklist)
- [ ] Token refresh view
- [ ] Profile CRUD views
- [ ] Email verification views
- [ ] Password reset views
- [ ] IsOwner permission
- [ ] IsEmailVerified permission

### Phase 5: URLs & Testing (Day 3-4)
- [ ] Configure URL routing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test with Postman/Thunder Client
- [ ] Document API endpoints

## 📦 Quick Install Commands

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install djangorestframework-simplejwt==5.3.1
pip install sendgrid==6.11.0
pip install django-cors-headers==4.3.1
pip install python-decouple==3.8

# Update requirements.txt
pip freeze > requirements.txt

# Create accounts app
python manage.py startapp accounts

# After model creation, run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🔑 Environment Variables Template

Create `backend/.env`:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@chatsift.com
SENDGRID_SANDBOX_MODE=True

# Frontend
FRONTEND_URL=http://localhost:3000

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🔌 API Endpoints Overview

### Authentication
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/register/` | No | User registration |
| POST | `/api/v1/auth/login/` | No | User login |
| POST | `/api/v1/auth/logout/` | Yes | User logout |
| POST | `/api/v1/auth/refresh/` | No | Refresh JWT token |

### Email Verification
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/email/verify/send/` | Yes | Send verification email |
| POST | `/api/v1/auth/email/verify/confirm/` | No | Verify email with token |
| GET | `/api/v1/auth/email/status/` | Yes | Check verification status |

### Password Reset
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/password/reset/` | No | Request password reset |
| POST | `/api/v1/auth/password/reset/confirm/` | No | Confirm password reset |

### User Profile
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/v1/users/me/` | Yes | Get current user |
| PATCH | `/api/v1/users/me/` | Yes | Update profile |
| DELETE | `/api/v1/users/me/` | Yes | Delete account |

## 🧪 Quick Test Commands

```bash
# Run all tests
python manage.py test accounts

# Run specific test file
python manage.py test accounts.tests.test_views

# Run with coverage
coverage run --source='accounts' manage.py test accounts
coverage report
coverage html

# Test API with curl
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test123!@#"}'
```

## 📊 File Structure Reference

```
backend/accounts/
├── __init__.py
├── admin.py              # Register models in admin
├── apps.py               # App configuration
├── models.py             # User, UserProfile models
├── managers.py           # Custom user manager
├── serializers.py        # All DRF serializers
├── views.py              # All API views
├── urls.py               # URL routing
├── permissions.py        # IsOwner, IsEmailVerified
├── validators.py         # Password validators
├── signals.py            # Auto-create UserProfile
├── utils.py              # Helper functions (email sending)
├── tokens.py             # Token generators
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_serializers.py
    ├── test_views.py
    └── test_permissions.py
```

## 🔐 Key Security Points

1. **Password Requirements:**
   - Minimum 8 characters
   - Must include: uppercase, lowercase, number, special character

2. **Token Expiry:**
   - Access token: 15 minutes
   - Refresh token: 7 days
   - Verification token: 24 hours
   - Password reset token: 1 hour

3. **Rate Limiting:**
   - Login: 5 attempts per 15 minutes
   - Registration: 3 per hour per IP
   - Email verification: 3 per hour per user
   - Password reset: 3 per hour per email

4. **Email Verification:**
   - Not required for signup
   - Required before creating integrations
   - Enforced by `IsEmailVerified` permission

## 📚 Documentation References

- **Implementation Plan:** [`ACCOUNTS_API_IMPLEMENTATION_PLAN.md`](backend/ACCOUNTS_API_IMPLEMENTATION_PLAN.md)
- **Flow Diagrams:** [`ACCOUNTS_API_FLOW.md`](backend/ACCOUNTS_API_FLOW.md)
- **Requirements:** [`ACCOUNTS_API_REQUIREMENTS.md`](backend/ACCOUNTS_API_REQUIREMENTS.md)
- **Architecture:** [`BACKEND_ARCHITECTURE.md`](backend/BACKEND_ARCHITECTURE.md)

## 🎯 Next Steps

After completing account APIs, implement in this order:

1. **Integrations App** - Platform connections (Discord, Telegram)
2. **Monitoring App** - Channel monitoring setup
3. **Messages App** - Message fetching and storage
4. **Summaries App** - AI-powered summarization
5. **Notifications App** - Delivery preferences

## 💡 Pro Tips

1. **Development Workflow:**
   - Use console email backend during development
   - Switch to SendGrid sandbox mode for testing
   - Enable production mode only when ready

2. **Testing Strategy:**
   - Write tests before implementation (TDD)
   - Test happy path and error cases
   - Mock external services (SendGrid)

3. **Git Workflow:**
   - Create feature branch: `git checkout -b feature/account-apis`
   - Commit frequently with clear messages
   - Push and create PR when complete

4. **Common Issues:**
   - Forgot to run migrations? → `python manage.py migrate`
   - Import errors? → Check `INSTALLED_APPS` in settings
   - Token errors? → Verify JWT configuration
   - Email not sending? → Check SendGrid API key

## 🚀 Ready to Implement?

Switch to **Code mode** to start implementation:

```
/mode code
```

Or continue planning if you need more details!