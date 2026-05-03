# 📚 Account APIs Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
Most endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 🔐 Authentication Endpoints

### 1. User Registration

**Endpoint:** `POST /auth/register/`

**Authentication:** Not required

**Description:** Register a new user account. Automatically creates a user profile and returns JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",  // optional
  "last_name": "Doe"     // optional
}
```

**Password Requirements:**
- Minimum 8 characters
- Must contain uppercase and lowercase letters
- Must contain at least one number
- Must contain at least one special character
- Cannot be too similar to username or email
- Cannot be a commonly used password

**Success Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "55b3749a-e141-4c44-90ce-ecc2b7e193b4",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "email_verified": false,
      "email_verified_at": null,
      "date_joined": "2026-05-02T12:06:35.174504Z",
      "last_login": null,
      "profile": {
        "timezone": "UTC",
        "preferred_summary_time": "09:00:00"
      }
    },
    "tokens": {
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  },
  "message": "User registered successfully"
}
```

**Error Responses:**

400 Bad Request - Validation errors:
```json
{
  "email": ["A user with this email already exists."],
  "username": ["A user with this username already exists."],
  "password_confirm": ["Passwords do not match."],
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common."
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

---

### 2. User Login

**Endpoint:** `POST /auth/login/`

**Authentication:** Not required

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "55b3749a-e141-4c44-90ce-ecc2b7e193b4",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "email_verified": false,
      "email_verified_at": null,
      "date_joined": "2026-05-02T12:06:35.174504Z",
      "last_login": "2026-05-02T12:06:45.542203Z",
      "profile": {
        "timezone": "UTC",
        "preferred_summary_time": "09:00:00"
      }
    },
    "tokens": {
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  },
  "message": "Login successful"
}
```

**Error Responses:**

400 Bad Request - Invalid credentials:
```json
{
  "non_field_errors": ["Invalid email or password."]
}
```

400 Bad Request - Inactive account:
```json
{
  "non_field_errors": ["User account is disabled."]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

---

### 3. Token Refresh

**Endpoint:** `POST /auth/refresh/`

**Authentication:** Not required (uses refresh token)

**Description:** Get a new access token using a refresh token. With rotation enabled, also returns a new refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**

401 Unauthorized - Invalid or expired token:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Token Lifetimes:**
- Access token: 15 minutes
- Refresh token: 7 days

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

---

### 4. User Logout

**Endpoint:** `POST /auth/logout/`

**Authentication:** Required (Bearer token)

**Description:** Logout user by blacklisting the refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

**Error Responses:**

400 Bad Request - Missing refresh token:
```json
{
  "status": "error",
  "message": "Refresh token is required"
}
```

400 Bad Request - Invalid token:
```json
{
  "status": "error",
  "message": "Invalid token"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

---

## 👤 User Profile Endpoints

### 5. Get Current User Profile

**Endpoint:** `GET /users/me/`

**Authentication:** Required (Bearer token)

**Description:** Retrieve the authenticated user's profile information.

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "55b3749a-e141-4c44-90ce-ecc2b7e193b4",
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": false,
    "email_verified_at": null,
    "date_joined": "2026-05-02T12:06:35.174504Z",
    "last_login": "2026-05-02T12:06:45.542203Z",
    "profile": {
      "timezone": "Asia/Calcutta",
      "preferred_summary_time": "08:00:00"
    }
  }
}
```

**Error Responses:**

401 Unauthorized - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer your_access_token"
```

---

### 6. Update User Profile

**Endpoint:** `PATCH /users/me/`

**Authentication:** Required (Bearer token)

**Description:** Update the authenticated user's profile. All fields are optional.

**Request Body:**
```json
{
  "username": "newusername",
  "first_name": "Updated",
  "last_name": "Name",
  "profile": {
    "timezone": "Asia/Calcutta",
    "preferred_summary_time": "08:00:00"
  }
}
```

**Available Timezones:** Any valid timezone from the IANA timezone database (e.g., "UTC", "Asia/Calcutta", "America/New_York", "Europe/London")

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "55b3749a-e141-4c44-90ce-ecc2b7e193b4",
    "email": "user@example.com",
    "username": "newusername",
    "first_name": "Updated",
    "last_name": "Name",
    "email_verified": false,
    "email_verified_at": null,
    "date_joined": "2026-05-02T12:06:35.174504Z",
    "last_login": "2026-05-02T12:06:45.542203Z",
    "profile": {
      "timezone": "Asia/Calcutta",
      "preferred_summary_time": "08:00:00"
    }
  },
  "message": "Profile updated successfully"
}
```

**Error Responses:**

400 Bad Request - Username already exists:
```json
{
  "username": ["A user with this username already exists."]
}
```

**cURL Example:**
```bash
curl -X PATCH http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "profile": {
      "timezone": "Asia/Calcutta",
      "preferred_summary_time": "08:00:00"
    }
  }'
```

---

### 7. Delete User Account

**Endpoint:** `DELETE /users/me/`

**Authentication:** Required (Bearer token)

**Description:** Soft delete the authenticated user's account (sets is_active to False).

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Account deleted successfully"
}
```

**Note:** This is a soft delete. The user account is deactivated but not permanently removed from the database.

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer your_access_token"
```

---

## 🔒 Security Features

### JWT Token Security
- **Access Token Lifetime:** 15 minutes
- **Refresh Token Lifetime:** 7 days
- **Token Rotation:** Enabled (new refresh token on each refresh)
- **Token Blacklisting:** Enabled (tokens blacklisted on logout)
- **Algorithm:** HS256

### Password Security
- Passwords are hashed using Django's PBKDF2 algorithm
- Minimum 8 characters required
- Must include uppercase, lowercase, numbers, and special characters
- Common password validation enabled
- User attribute similarity validation enabled

### CORS Configuration
- Configured for localhost:3000 (frontend)
- Credentials allowed for cookie-based auth (if needed)

---

## 📊 Response Format

### Success Response Structure
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response Structure
```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

Or for non-field errors:
```json
{
  "non_field_errors": ["Error message"]
}
```

Or for detail errors:
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

---

## 🧪 Testing the APIs

### Using cURL

1. **Register a user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"TestPass123!","password_confirm":"TestPass123!"}'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

3. **Get profile (save access token from login):**
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(f"{BASE_URL}/auth/register/", json={
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
})
data = response.json()
access_token = data['data']['tokens']['access']

# Get profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
print(response.json())
```

---

## 🚀 Next Steps

The following features are planned but not yet implemented:

1. **Email Verification**
   - `POST /auth/email/verify/send/` - Send verification email
   - `POST /auth/email/verify/confirm/` - Verify email with token
   - `GET /auth/email/status/` - Check verification status

2. **Password Reset**
   - `POST /auth/password/reset/` - Request password reset
   - `POST /auth/password/reset/confirm/` - Confirm password reset

3. **Email Integration**
   - SendGrid configuration for production emails
   - Email templates for verification and password reset

---

## 📝 Notes

- All timestamps are in ISO 8601 format with UTC timezone
- UUIDs are used for user IDs instead of sequential integers
- Email addresses are stored in lowercase
- User profiles are automatically created when users register
- The API uses Django REST Framework's browsable API at `/api/v1/`

---

**Last Updated:** May 2, 2026
**API Version:** 1.0
**Django Version:** 6.0.4
**DRF Version:** 3.17.1