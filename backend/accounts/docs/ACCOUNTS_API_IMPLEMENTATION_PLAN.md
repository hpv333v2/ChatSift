# 📋 Account APIs Implementation Plan

## 🎯 Overview
This document outlines the detailed implementation plan for the ChatSift account management and authentication APIs, following the architecture defined in [`BACKEND_ARCHITECTURE.md`](backend/BACKEND_ARCHITECTURE.md).

## 📊 Current State Analysis

### Existing Setup
- ✅ Django 6.0.4 installed
- ✅ Django REST Framework 3.17.1 installed
- ✅ SQLite database configured
- ✅ Basic Django project structure (`Infobyte`)
- ❌ No accounts app created yet
- ❌ No JWT authentication configured
- ❌ No custom user model implemented

### Required Dependencies
```txt
djangorestframework-simplejwt==5.3.1  # JWT authentication
django-cors-headers==4.3.1            # CORS support for frontend
```

## 🗂️ App Structure

### accounts App Directory Layout
```
backend/accounts/
├── __init__.py
├── admin.py                    # Django admin configuration
├── apps.py                     # App configuration
├── models.py                   # User and UserProfile models
├── serializers.py              # DRF serializers
├── views.py                    # API views
├── urls.py                     # URL routing
├── permissions.py              # Custom permissions
├── managers.py                 # Custom user manager
├── validators.py               # Custom validators
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
└── migrations/
    └── __init__.py
```

## 🗄️ Database Models

### 1. Custom User Model
**File:** [`accounts/models.py`](backend/accounts/models.py)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """Custom user model with UUID primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
```

### 2. UserProfile Model
**File:** [`accounts/models.py`](backend/accounts/models.py)

```python
class UserProfile(models.Model):
    """Extended user profile with preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_summary_time = models.TimeField(default='09:00:00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
```

## 🔐 Authentication Configuration

### Django Settings Updates
**File:** [`backend/Infobyte/settings.py`](backend/Infobyte/settings.py)

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'accounts',
]

# Add CORS middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ... existing middleware
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'accounts.utils.custom_exception_handler',
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

# CORS settings (for development)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# Email configuration (for password reset)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

## 🔌 API Endpoints Implementation

### 1. User Registration
**Endpoint:** `POST /api/v1/auth/register/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "username": "johndoe",
      "date_joined": "2026-05-02T10:00:00Z"
    },
    "tokens": {
      "access": "access-token-here",
      "refresh": "refresh-token-here"
    }
  },
  "message": "User registered successfully"
}
```

### 2. User Login
**Endpoint:** `POST /api/v1/auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "username": "johndoe"
    },
    "tokens": {
      "access": "access-token-here",
      "refresh": "refresh-token-here"
    }
  },
  "message": "Login successful"
}
```

### 3. Token Refresh
**Endpoint:** `POST /api/v1/auth/refresh/`

**Request Body:**
```json
{
  "refresh": "refresh-token-here"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access": "new-access-token-here",
    "refresh": "new-refresh-token-here"
  }
}
```

### 4. User Logout
**Endpoint:** `POST /api/v1/auth/logout/`

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**
```json
{
  "refresh": "refresh-token-here"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### 5. Password Reset Request
**Endpoint:** `POST /api/v1/auth/password/reset/`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Password reset email sent"
}
```

### 6. Password Reset Confirm
**Endpoint:** `POST /api/v1/auth/password/reset/confirm/`

**Request Body:**
```json
{
  "token": "reset-token-here",
  "uid": "user-id-base64",
  "new_password": "NewSecurePass123!",
  "new_password_confirm": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Password reset successful"
}
```

### 7. Get Current User Profile
**Endpoint:** `GET /api/v1/users/me/`

**Headers:** `Authorization: Bearer <access-token>`

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "johndoe",
    "profile": {
      "timezone": "Asia/Calcutta",
      "preferred_summary_time": "09:00:00"
    },
    "date_joined": "2026-05-02T10:00:00Z",
    "last_login": "2026-05-02T11:00:00Z"
  }
}
```

### 8. Update User Profile
**Endpoint:** `PATCH /api/v1/users/me/`

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**
```json
{
  "username": "newusername",
  "profile": {
    "timezone": "America/New_York",
    "preferred_summary_time": "08:00:00"
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "newusername",
    "profile": {
      "timezone": "America/New_York",
      "preferred_summary_time": "08:00:00"
    }
  },
  "message": "Profile updated successfully"
}
```

### 9. Delete User Account
**Endpoint:** `DELETE /api/v1/users/me/`

**Headers:** `Authorization: Bearer <access-token>`

**Response (204 No Content)**

## 🛡️ Security Considerations

### Password Validation
- Minimum 8 characters
- Must contain uppercase, lowercase, number, and special character
- Cannot be similar to username or email
- Cannot be a common password

### Rate Limiting
- Login attempts: 5 per 15 minutes per IP
- Registration: 3 per hour per IP
- Password reset: 3 per hour per email

### Token Security
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Tokens are blacklisted on logout
- Refresh token rotation enabled

## 🧪 Testing Strategy

### Unit Tests
- Model validation and constraints
- Serializer validation logic
- Custom permission classes
- Password validators

### Integration Tests
- Registration flow
- Login/logout flow
- Token refresh flow
- Password reset flow
- Profile CRUD operations

### Test Coverage Target
- Minimum 80% code coverage
- 100% coverage for authentication logic

## 📝 Implementation Checklist

### Phase 1: Setup & Models
- [ ] Install required dependencies
- [ ] Create accounts app
- [ ] Implement custom User model
- [ ] Implement UserProfile model
- [ ] Create custom user manager
- [ ] Configure AUTH_USER_MODEL in settings
- [ ] Run initial migrations

### Phase 2: Serializers & Validators
- [ ] Create UserRegistrationSerializer
- [ ] Create UserLoginSerializer
- [ ] Create UserProfileSerializer
- [ ] Create password validators
- [ ] Implement custom validation logic

### Phase 3: Views & Permissions
- [ ] Implement registration view
- [ ] Implement login view
- [ ] Implement logout view
- [ ] Implement token refresh view
- [ ] Implement password reset views
- [ ] Implement user profile views (GET, PATCH, DELETE)
- [ ] Create IsOwner permission class

### Phase 4: URL Configuration
- [ ] Configure accounts app URLs
- [ ] Integrate with main project URLs
- [ ] Test all endpoint routes

### Phase 5: Testing & Documentation
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create API documentation
- [ ] Test with Postman/Thunder Client

## 🔄 Database Migration Strategy

### Migration Order
1. Create accounts app
2. Create User model migration
3. Create UserProfile model migration
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`

### Rollback Plan
- Keep backup of db.sqlite3 before migrations
- Document migration dependencies
- Test migrations in development first

## 📚 API Documentation Format

### Using Django REST Framework Browsable API
- Automatic documentation at `/api/v1/`
- Interactive API testing interface
- Schema generation support

### Additional Documentation
- Create OpenAPI/Swagger schema
- Generate Postman collection
- Write usage examples in README

## 🚀 Next Steps After Account APIs

1. **Integrations App** - Platform connections (Discord, Telegram)
2. **Monitoring App** - Channel monitoring configuration
3. **Messages App** - Message fetching and storage
4. **Summaries App** - AI-powered summarization
5. **Notifications App** - Delivery preferences and logs

## 📊 Success Metrics

- [ ] All 9 endpoints functional
- [ ] JWT authentication working
- [ ] Password reset emails sending
- [ ] Profile CRUD operations complete
- [ ] 80%+ test coverage
- [ ] API documentation complete
- [ ] Zero security vulnerabilities

---

**Implementation Timeline:** 2-3 days
**Priority:** High (Foundation for all other features)
**Dependencies:** None (First module to implement)