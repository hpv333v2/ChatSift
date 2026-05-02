# 🔄 Account APIs Flow Diagrams

## 1. User Registration Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Serializer
    participant Database
    participant JWT

    Client->>API: POST /api/v1/auth/register/
    Note over Client,API: {email, username, password}
    
    API->>Serializer: Validate registration data
    Serializer->>Serializer: Check password strength
    Serializer->>Serializer: Verify email uniqueness
    Serializer->>Serializer: Verify username uniqueness
    
    alt Validation Success
        Serializer->>Database: Create User
        Database->>Database: Create UserProfile (signal)
        Database-->>Serializer: User created
        Serializer->>JWT: Generate tokens
        JWT-->>Serializer: Access + Refresh tokens
        Serializer-->>API: User data + tokens
        API-->>Client: 201 Created
    else Validation Failed
        Serializer-->>API: Validation errors
        API-->>Client: 400 Bad Request
    end
```

## 2. User Login Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    participant JWT

    Client->>API: POST /api/v1/auth/login/
    Note over Client,API: {email, password}
    
    API->>Database: Find user by email
    
    alt User Found
        Database-->>API: User object
        API->>API: Verify password
        
        alt Password Valid
            API->>Database: Update last_login
            API->>JWT: Generate tokens
            JWT-->>API: Access + Refresh tokens
            API-->>Client: 200 OK with tokens
        else Password Invalid
            API-->>Client: 401 Unauthorized
        end
    else User Not Found
        API-->>Client: 401 Unauthorized
    end
```

## 3. Token Refresh Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant JWT
    participant Blacklist

    Client->>API: POST /api/v1/auth/refresh/
    Note over Client,API: {refresh: token}
    
    API->>JWT: Validate refresh token
    JWT->>Blacklist: Check if blacklisted
    
    alt Token Valid & Not Blacklisted
        Blacklist-->>JWT: Not blacklisted
        JWT->>JWT: Generate new access token
        JWT->>JWT: Rotate refresh token
        JWT->>Blacklist: Blacklist old refresh token
        JWT-->>API: New tokens
        API-->>Client: 200 OK with new tokens
    else Token Invalid or Blacklisted
        JWT-->>API: Invalid token
        API-->>Client: 401 Unauthorized
    end
```

## 4. Password Reset Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    participant Email
    participant TokenGen

    Note over Client,API: Step 1: Request Reset
    Client->>API: POST /api/v1/auth/password/reset/
    Note over Client,API: {email}
    
    API->>Database: Find user by email
    
    alt User Found
        Database-->>API: User object
        API->>TokenGen: Generate reset token
        TokenGen-->>API: Token + UID
        API->>Email: Send reset email
        Email-->>Client: Email sent
        API-->>Client: 200 OK
    else User Not Found
        Note over API: Still return 200 (security)
        API-->>Client: 200 OK
    end

    Note over Client,API: Step 2: Confirm Reset
    Client->>API: POST /api/v1/auth/password/reset/confirm/
    Note over Client,API: {token, uid, new_password}
    
    API->>TokenGen: Validate token + UID
    
    alt Token Valid
        TokenGen-->>API: Valid
        API->>Database: Update password
        Database-->>API: Password updated
        API-->>Client: 200 OK
    else Token Invalid
        TokenGen-->>API: Invalid
        API-->>Client: 400 Bad Request
    end
```

## 5. Profile Management Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Database

    Note over Client,API: Get Profile
    Client->>API: GET /api/v1/users/me/
    Note over Client,API: Authorization: Bearer token
    
    API->>Auth: Validate JWT token
    
    alt Token Valid
        Auth-->>API: User authenticated
        API->>Database: Get user + profile
        Database-->>API: User data
        API-->>Client: 200 OK with profile
    else Token Invalid
        Auth-->>API: Unauthorized
        API-->>Client: 401 Unauthorized
    end

    Note over Client,API: Update Profile
    Client->>API: PATCH /api/v1/users/me/
    Note over Client,API: {username, profile: {...}}
    
    API->>Auth: Validate JWT token
    Auth-->>API: User authenticated
    API->>Database: Update user + profile
    Database-->>API: Updated data
    API-->>Client: 200 OK

    Note over Client,API: Delete Account
    Client->>API: DELETE /api/v1/users/me/
    API->>Auth: Validate JWT token
    Auth-->>API: User authenticated
    API->>Database: Soft delete user
    Database-->>API: Deleted
    API-->>Client: 204 No Content
```

## 6. Authentication Middleware Flow

```mermaid
flowchart TD
    A[Incoming Request] --> B{Has Authorization Header?}
    B -->|No| C[Return 401 Unauthorized]
    B -->|Yes| D[Extract JWT Token]
    D --> E{Token Valid?}
    E -->|No| F[Return 401 Unauthorized]
    E -->|Yes| G{Token Expired?}
    G -->|Yes| H[Return 401 Token Expired]
    G -->|No| I{Token Blacklisted?}
    I -->|Yes| J[Return 401 Token Invalid]
    I -->|No| K[Get User from Token]
    K --> L{User Active?}
    L -->|No| M[Return 401 User Inactive]
    L -->|Yes| N[Attach User to Request]
    N --> O[Process Request]
    O --> P[Return Response]
```

## 7. Permission Check Flow

```mermaid
flowchart TD
    A[API View Called] --> B{User Authenticated?}
    B -->|No| C[Return 401]
    B -->|Yes| D{Check View Permissions}
    D --> E{IsOwner Required?}
    E -->|Yes| F{Resource Belongs to User?}
    F -->|No| G[Return 403 Forbidden]
    F -->|Yes| H[Allow Access]
    E -->|No| H
    H --> I[Execute View Logic]
    I --> J[Return Response]
```

## 8. Database Schema Relationships

```mermaid
erDiagram
    USER ||--|| USER_PROFILE : has
    USER {
        uuid id PK
        string email UK
        string username UK
        string password
        boolean is_active
        datetime date_joined
        datetime last_login
    }
    USER_PROFILE {
        uuid id PK
        uuid user_id FK
        string timezone
        time preferred_summary_time
        datetime created_at
        datetime updated_at
    }
```

## 9. Error Handling Flow

```mermaid
flowchart TD
    A[Request Received] --> B{Try Execute}
    B -->|Success| C[Return Success Response]
    B -->|Exception| D{Exception Type}
    D -->|ValidationError| E[Return 400 Bad Request]
    D -->|AuthenticationFailed| F[Return 401 Unauthorized]
    D -->|PermissionDenied| G[Return 403 Forbidden]
    D -->|NotFound| H[Return 404 Not Found]
    D -->|Other| I[Log Error]
    I --> J[Return 500 Internal Server Error]
```

## 10. Complete User Journey

```mermaid
stateDiagram-v2
    [*] --> Anonymous
    Anonymous --> Registered: POST /auth/register/
    Registered --> LoggedIn: POST /auth/login/
    LoggedIn --> ViewingProfile: GET /users/me/
    ViewingProfile --> UpdatingProfile: PATCH /users/me/
    UpdatingProfile --> ViewingProfile
    LoggedIn --> TokenExpired: Access token expires
    TokenExpired --> LoggedIn: POST /auth/refresh/
    LoggedIn --> LoggedOut: POST /auth/logout/
    LoggedOut --> Anonymous
    Anonymous --> PasswordResetRequested: POST /auth/password/reset/
    PasswordResetRequested --> PasswordReset: POST /auth/password/reset/confirm/
    PasswordReset --> Anonymous
    LoggedIn --> AccountDeleted: DELETE /users/me/
    AccountDeleted --> [*]
```

## Key Implementation Notes

### 1. Signal Handlers
- Automatically create UserProfile when User is created
- Send welcome email on registration
- Log authentication events

### 2. Token Management
- Access tokens stored in memory (client-side)
- Refresh tokens can be stored in httpOnly cookies
- Blacklist tokens on logout for security

### 3. Security Best Practices
- Always hash passwords using Django's built-in hasher
- Rate limit authentication endpoints
- Use HTTPS in production
- Implement CSRF protection
- Validate all user inputs

### 4. Error Messages
- Generic messages for authentication failures (security)
- Detailed validation errors for registration
- Clear messages for token expiration

### 5. Testing Scenarios
- Valid registration with all fields
- Registration with duplicate email/username
- Login with correct/incorrect credentials
- Token refresh with valid/invalid tokens
- Password reset with valid/invalid tokens
- Profile updates with valid/invalid data
- Account deletion with active sessions