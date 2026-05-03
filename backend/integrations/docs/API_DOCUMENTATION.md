# Integrations API Documentation

Complete API reference for the ChatSift Integrations app.

## Base URL

```
http://localhost:8000/api/v1/integrations/
```

## Authentication

All endpoints (except OAuth callbacks) require JWT authentication.

```http
Authorization: Bearer <access_token>
```

Get access token from `/api/v1/auth/login/` endpoint.

## Table of Contents

1. [Discord Integration](#discord-integration)
2. [Telegram Integration](#telegram-integration)
3. [Connection Management](#connection-management)
4. [Error Responses](#error-responses)

---

## Discord Integration

### 1. Get Discord Authorization URL

Generate OAuth URL for Discord authorization.

**Endpoint:** `GET /discord/authorize/`

**Authentication:** Required

**Permissions:** Email must be verified

**Response:**
```json
{
  "status": "success",
  "data": {
    "authorization_url": "https://discord.com/api/oauth2/authorize?...",
    "state": "random-csrf-token"
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/integrations/discord/authorize/
```

---

### 2. Discord OAuth Callback

Handle Discord OAuth callback (called by Discord, not directly).

**Endpoint:** `GET /discord/callback/`

**Authentication:** Required

**Query Parameters:**
- `code` (required): Authorization code from Discord
- `state` (required): CSRF token from authorization request

**Response:**
```json
{
  "status": "success",
  "data": {
    "connection": {
      "id": "uuid",
      "platform": "discord",
      "platform_user_id": "123456789",
      "platform_username": "username#1234",
      "status": "active",
      "channels_count": 5,
      "created_at": "2026-05-02T12:00:00Z"
    }
  },
  "message": "Discord connected successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid state or code
- `403 Forbidden`: Email not verified
- `500 Internal Server Error`: Discord API error

---

## Telegram Integration

### 3. Connect Telegram Bot

Connect a Telegram bot using bot token.

**Endpoint:** `POST /telegram/connect/`

**Authentication:** Required

**Permissions:** Email must be verified

**Request Body:**
```json
{
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "connection": {
      "id": "uuid",
      "platform": "telegram",
      "platform_user_id": "123456789",
      "platform_username": "my_bot",
      "status": "active",
      "channels_count": 3,
      "created_at": "2026-05-02T12:00:00Z"
    }
  },
  "message": "Telegram bot connected successfully"
}
```

**Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"bot_token":"123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"}' \
     http://localhost:8000/api/v1/integrations/telegram/connect/
```

**Error Responses:**
- `400 Bad Request`: Invalid bot token format or bot validation failed
- `403 Forbidden`: Email not verified
- `409 Conflict`: Bot already connected

---

## Connection Management

### 4. List Connections

Get all connections for the authenticated user.

**Endpoint:** `GET /`

**Authentication:** Required

**Response:**
```json
{
  "status": "success",
  "data": {
    "connections": [
      {
        "id": "uuid",
        "platform": "discord",
        "platform_user_id": "123456789",
        "platform_username": "username#1234",
        "status": "active",
        "channels_count": 5,
        "is_token_expired": false,
        "last_synced": "2026-05-02T12:00:00Z",
        "created_at": "2026-05-01T10:00:00Z"
      },
      {
        "id": "uuid",
        "platform": "telegram",
        "platform_user_id": "987654321",
        "platform_username": "my_bot",
        "status": "active",
        "channels_count": 3,
        "is_token_expired": false,
        "last_synced": "2026-05-02T11:30:00Z",
        "created_at": "2026-05-01T11:00:00Z"
      }
    ],
    "total": 2
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/integrations/
```

---

### 5. Get Connection Details

Get detailed information about a specific connection including channels.

**Endpoint:** `GET /{connection_id}/`

**Authentication:** Required

**Permissions:** Must own the connection

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "platform": "discord",
    "platform_user_id": "123456789",
    "platform_username": "username#1234",
    "status": "active",
    "channels_count": 2,
    "is_token_expired": false,
    "last_synced": "2026-05-02T12:00:00Z",
    "created_at": "2026-05-01T10:00:00Z",
    "channels": [
      {
        "id": "uuid",
        "channel_id": "987654321",
        "channel_name": "My Server",
        "channel_type": "discord_guild",
        "is_active": true,
        "permissions": ["read", "write"],
        "created_at": "2026-05-01T10:00:00Z"
      },
      {
        "id": "uuid",
        "channel_id": "123456789",
        "channel_name": "general",
        "channel_type": "discord_channel",
        "parent_channel_id": "987654321",
        "is_active": true,
        "permissions": ["read", "write"],
        "created_at": "2026-05-01T10:00:00Z"
      }
    ]
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/integrations/{connection_id}/
```

**Error Responses:**
- `403 Forbidden`: Not the connection owner
- `404 Not Found`: Connection doesn't exist

---

### 6. Delete Connection

Remove a connection and all associated channels.

**Endpoint:** `DELETE /{connection_id}/`

**Authentication:** Required

**Permissions:** Must own the connection

**Response:**
```json
{
  "status": "success",
  "message": "Connection deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/integrations/{connection_id}/
```

**Error Responses:**
- `403 Forbidden`: Not the connection owner
- `404 Not Found`: Connection doesn't exist

---

### 7. Refresh Connection

Manually trigger channel sync for a connection.

**Endpoint:** `POST /{connection_id}/refresh/`

**Authentication:** Required

**Permissions:** Must own the connection

**Response:**
```json
{
  "status": "success",
  "data": {
    "channels_synced": 5,
    "channels_added": 2,
    "channels_removed": 1,
    "channels_updated": 2
  },
  "message": "Channels synced successfully"
}
```

**Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/integrations/{connection_id}/refresh/
```

**Error Responses:**
- `403 Forbidden`: Not the connection owner
- `404 Not Found`: Connection doesn't exist
- `500 Internal Server Error`: Sync failed

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

### Common Error Messages

**Authentication Errors:**
```json
{
  "status": "error",
  "message": "Authentication credentials were not provided"
}
```

**Permission Errors:**
```json
{
  "status": "error",
  "message": "Email verification required to create integrations"
}
```

**Validation Errors:**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "bot_token": ["Invalid bot token format"]
  }
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Discord OAuth**: 10 requests per minute per user
- **Telegram Connect**: 5 requests per minute per user
- **Connection Management**: 60 requests per minute per user
- **Refresh**: 10 requests per minute per connection

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1651507200
```

---

## Webhooks (Future Feature)

Webhook support for real-time updates is planned for future releases.

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List connections
response = requests.get(f"{BASE_URL}/integrations/", headers=headers)
connections = response.json()

# Connect Telegram bot
data = {"bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"}
response = requests.post(
    f"{BASE_URL}/integrations/telegram/connect/",
    headers=headers,
    json=data
)
connection = response.json()

# Refresh connection
response = requests.post(
    f"{BASE_URL}/integrations/{connection_id}/refresh/",
    headers=headers
)
result = response.json()
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your_jwt_token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// List connections
const response = await fetch(`${BASE_URL}/integrations/`, { headers });
const connections = await response.json();

// Connect Telegram bot
const data = { bot_token: '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11' };
const response = await fetch(`${BASE_URL}/integrations/telegram/connect/`, {
  method: 'POST',
  headers,
  body: JSON.stringify(data)
});
const connection = await response.json();

// Refresh connection
const response = await fetch(
  `${BASE_URL}/integrations/${connectionId}/refresh/`,
  { method: 'POST', headers }
);
const result = await response.json();
```

---

## Testing

Use the provided Postman collection or test with curl:

```bash
# Set your token
export TOKEN="your_jwt_token_here"

# Test endpoints
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/integrations/discord/authorize/
```

---

## Support

For issues or questions:
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for setup help
- Review [CELERY_SETUP.md](../CELERY_SETUP.md) for background tasks
- Check application logs for errors

## Made with Bob