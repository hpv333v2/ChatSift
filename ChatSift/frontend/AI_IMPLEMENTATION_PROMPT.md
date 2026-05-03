# ChatSift Frontend — Production Implementation Prompt

> Generate complete, production-ready frontend code for the entire ChatSift application.

---

## 0. Identity & Source of Truth

- **Product**: ChatSift — AI-powered group-chat summarization (Discord + Telegram → daily AI digests).
- **Django project name**: `Infobyte` (do not rename — README says "ChatSift", Django says "Infobyte"; this is intentional).
- **Backend status**: Built and running locally at `http://localhost:8000/api/v1/`. Stack: Django 6.0.4 + DRF 3.17 + SimpleJWT 5.3 + SQLite + `encrypted_model_fields` for OAuth tokens.
- **Frontend status**: Empty. You are creating it from zero.
- **Source of truth (STRICT)**: Use this document and the four backend files referenced below. Do **NOT** invent endpoints, fields, request bodies, or response shapes. If a field is not in this prompt, flag it in section 9 "Missing backend gaps" — do **NOT** guess.
  - `backend/Infobyte/urls.py`
  - `backend/Infobyte/settings.py`
  - `backend/accounts/{urls,views,serializers,models}.py`
  - `backend/integrations/{urls,views,serializers,models}.py`

---

## 1. Stack (Locked)

- **Framework**: React Native 0.73.2 + React Native Web 0.19.9 via **Expo SDK ~50** (managed workflow, single codebase for Web + iOS + Android).
- **Language**: TypeScript 5.3.x, strict mode.
- **UI**: `react-native-paper` ^5.12 (Material Design 3), `react-native-vector-icons` ^10, `react-native-reanimated` ~3.6, `react-native-safe-area-context` 4.8, `react-native-screens` ~3.29.
- **Navigation**: `@react-navigation/native` ^6.1, `@react-navigation/native-stack` ^6.9, `@react-navigation/bottom-tabs` ^6.5.
- **Server state**: `@tanstack/react-query` ^5.17.
- **Client state**: `zustand` ^4.5.
- **HTTP**: `axios` ^1.6.
- **Forms**: `react-hook-form` ^7.49 + `zod` ^3.22 + `@hookform/resolvers`.
- **Storage**: `@react-native-async-storage/async-storage` ^1.21.
- **Utils**: `date-fns` ^3, `jwt-decode` ^4.

Do **not** add other dependencies without flagging them in section 9.

---

## 2. Backend Contract (EXACT — pulled from backend code)

### 2.1 Base & Auth
- **Base URL**: `http://localhost:8000/api/v1`
- **Auth scheme**: `Authorization: Bearer <access>` (SimpleJWT, HS256).
- **Token lifetimes**: access 15 min, refresh 7 days; refresh tokens **rotate** and old ones are blacklisted on rotation.
- **CORS allowed origins**: `http://localhost:3000`, `http://127.0.0.1:3000` only. Run web dev server on **port 3000**.
- **Default pagination**: DRF `PageNumberPagination`, `PAGE_SIZE = 20`. Paginated responses have shape `{ count, next, previous, results }` (DRF default — note: this is **not** wrapped in `{status, data}`).
- **Response envelope (non-paginated)**: most endpoints return `{ "status": "success" | "error" | "info", "data": {...}, "message": "..." }`. Token-refresh endpoint is a SimpleJWT exception — see 2.2.

### 2.2 Authentication & User Endpoints (`accounts` app — IMPLEMENTED)

#### `POST /auth/register/` — public
Request:
```json
{ "email": "u@x.com", "username": "jdoe", "password": "Pass123!@#",
  "password_confirm": "Pass123!@#", "first_name": "J", "last_name": "D" }
```
- `first_name`, `last_name` optional. Email lower-cased server-side. Password validated by Django's default validators (UserAttributeSimilarity, MinimumLength=8, CommonPassword, NumericPassword).

Response `201`:
```json
{ "status": "success",
  "data": { "user": <User>, "tokens": { "refresh": "...", "access": "..." } },
  "message": "User registered successfully" }
```
Validation errors return DRF default `400` with field-keyed arrays (e.g. `{"password": ["..."], "password_confirm": ["Passwords do not match."]}`).

#### `POST /auth/login/` — public
Request: `{ "email": "u@x.com", "password": "..." }`
Response `200`: `{ "status": "success", "data": { "user": <User>, "tokens": { "refresh", "access" } }, "message": "Login successful" }`
Errors: `400` with non-field errors `["Invalid email or password."]` or `["User account is disabled."]`.

#### `POST /auth/logout/` — auth required
Request: `{ "refresh": "..." }`
Response `200`: `{ "status": "success", "message": "Logout successful" }`. Blacklists the refresh token.

#### `POST /auth/refresh/` — public (SimpleJWT default — **NOT** wrapped)
Request: `{ "refresh": "..." }`
Response `200`: `{ "access": "...", "refresh": "..." }` (refresh present because `ROTATE_REFRESH_TOKENS=True`).

#### `POST /auth/email/verify/send/` — auth required
Request: empty body. Sends link to `request.user.email`.
Response `200`: `{ "status": "success" | "info", "message": "..." }`. Uses Django console email backend in dev — link prints to backend console.

#### `POST /auth/email/verify/confirm/` — public
Request: `{ "token": "...", "uid": "..." }` (both from email link).
Response `200`: `{ "status": "success", "message": "Email verified successfully", "data": { "email_verified": true, "email_verified_at": "<ISO>" } }`. Errors: `400` with `{"status":"error","message":"Invalid or expired verification link"}`.

#### `GET /auth/email/status/` — auth required
Response `200`: `{ "status":"success", "data": { "email", "email_verified": bool, "email_verified_at": "<ISO>|null", "can_create_integrations": bool } }`. **Frontend gate**: `can_create_integrations === false` blocks all integration endpoints with a 403 from `IsEmailVerified` permission — show a "verify email" call-to-action.

#### `GET /users/me/` — auth required
Response `200`: `{ "status":"success", "data": <User> }`

#### `PATCH /users/me/` — auth required
Request (all optional): `{ "username", "first_name", "last_name", "profile": { "timezone", "preferred_summary_time" } }`. `preferred_summary_time` is `"HH:MM:SS"`.
Response `200`: `{ "status":"success", "data": <User>, "message": "Profile updated successfully" }`

#### `DELETE /users/me/` — auth required (soft delete: sets `is_active=false`)
Response `200`: `{ "status":"success", "message":"Account deleted successfully" }`

#### `<User>` shape (read):
```ts
{
  id: string;           // UUID
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  email_verified: boolean;
  email_verified_at: string | null;  // ISO 8601
  date_joined: string;               // ISO 8601
  last_login: string | null;         // ISO 8601
  profile: { timezone: string; preferred_summary_time: string /* "HH:MM:SS" */ } | null;
}
```

### 2.3 Integrations Endpoints (`integrations` app — IMPLEMENTED, **with URL bug — see §9**)

> **⚠️ URL routing bug in backend** ([Infobyte/urls.py](../backend/Infobyte/urls.py)): the integrations urlconf is mounted at `path('api/v1/', include('integrations.urls'))` instead of `path('api/v1/integrations/', ...)`. The integrations sub-routes have **no `integrations/` prefix**, so the live URLs are at `/api/v1/discord/authorize/`, `/api/v1/<uuid>/`, etc., which collides with `/api/v1/users/me/`. This is broken in production. **Use the intended paths below** (`/api/v1/integrations/...`) and flag the fix in §9 — the user must fix the backend urlconf before this frontend works. Do **not** code around the bug.

All require `IsAuthenticated` AND `IsEmailVerified` (returns `403` if `email_verified=false`).

#### `GET /integrations/discord/authorize/`
Response `200`: `{ "status":"success", "data": { "authorization_url": "https://discord.com/..." } }`. Frontend opens this URL; backend stores OAuth `state` in Django session.

#### `GET /integrations/discord/callback/?code=...&state=...`
Backend validates state and exchanges code. Response `200|201`: `{ "status":"success", "data": <PlatformConnection>, "message":"Discord connected successfully" }`.
**Note**: this is browser-redirect-driven; on web, Discord redirects directly to backend, which currently returns JSON. The mobile flow needs to be deep-linked back. Flag UX in §9.

#### `POST /integrations/telegram/connect/`
Request: `{ "bot_token": "123456:ABC-..." }` (40–50 chars, must contain `:`, prefix must be numeric).
Response `200|201`: `{ "status":"success", "data": <PlatformConnection>, "message":"Telegram bot connected successfully" }`.

#### `GET /integrations/`
Response `200`: `{ "status":"success", "data": { "connections": [<PlatformConnection>, ...] } }`. **Not** paginated (uses custom `list()`).

#### `GET /integrations/<uuid:id>/`
Response `200`: `{ "status":"success", "data": <PlatformConnectionDetail> }` (includes `channels` array).

#### `DELETE /integrations/<uuid:id>/`
Response `200`: `{ "status":"success", "message":"Connection deleted successfully" }`.

#### `POST /integrations/<uuid:id>/refresh/`
Refreshes OAuth token (Discord) and re-syncs channels.
Response `200`: `{ "status":"success", "data": { "channels_synced": int, "channels_added": int, "channels_removed": int, "last_sync": "<ISO>" }, "message":"Connection refreshed successfully" }`.

#### `<PlatformConnection>` shape:
```ts
{
  id: string;                      // UUID
  platform: "discord" | "telegram";
  platform_display: "Discord" | "Telegram";
  platform_user_id: string;
  platform_username: string;
  status: "active" | "expired" | "revoked" | "error";
  status_display: string;
  is_token_expired: boolean;
  last_sync: string | null;        // ISO 8601
  error_message: string | null;
  channels_count: number;          // active channels
  created_at: string;              // ISO 8601
  updated_at: string;              // ISO 8601
  // PlatformConnectionDetail also has:
  channels?: Channel[];
}
```

#### `<Channel>` shape:
```ts
{
  id: string;                      // UUID
  channel_id: string;              // platform-specific
  channel_name: string;
  channel_type: "discord_server" | "discord_channel" | "telegram_group" | "telegram_channel";
  platform: "discord" | "telegram";
  member_count: number | null;
  icon_url: string | null;
  description: string | null;
  can_read_messages: boolean;
  can_read_history: boolean;
  is_active: boolean;
  last_synced: string | null;      // ISO 8601
  created_at: string;              // ISO 8601
}
```

### 2.4 Monitoring, Summaries, Notifications, Chats Apps — **NOT YET WIRED**

Apps `monitoring`, `summaries`, `notifications`, `chats` exist in `INSTALLED_APPS` but have **no `urls.py` included** in `Infobyte/urls.py`. **Do not call any monitoring/summary/notification endpoint.** Render screens for these features in a polished **"Coming Soon"** state per §5.5.

---

## 3. Global UI Behavior (must implement)

- **Authentication flow**: register → auto-login (tokens returned in register response) → email-verify nag banner → main app. Token state persisted via AsyncStorage. App boot reads `auth_tokens`, hits `GET /users/me/` to validate, routes to Auth or Main stack accordingly.
- **Token refresh**: axios response interceptor on `401`: call `/auth/refresh/` once, replace stored tokens (note rotation), retry original request. On refresh failure → clear storage → kick to Login.
- **Fetch & render** every implemented endpoint listed in §2.
- **Loading / error / empty / unauthorized / email-not-verified** states for every screen and list.
- **Forms**: react-hook-form + zod schemas matching backend validators (email, password ≥8 chars, etc.). Show server-side field errors next to inputs; non-field errors as Snackbar.
- **Navigation**: Auth stack (Login, Register, EmailVerification) and Main app (Dashboard, Integrations, IntegrationDetail, Monitoring [Coming Soon], Summaries [Coming Soon], Settings).
- **Data refresh**: React Query default `staleTime: 60_000`, `refetchOnWindowFocus: true` on web, pull-to-refresh on native. Mutations invalidate relevant query keys (`['integrations']`, `['user', 'me']`, `['emailStatus']`).
- **Toast/Snackbar** for all mutation success/error.

---

## 4. Responsive Requirements

- **Mobile-first**, scales mobile → tablet → desktop → ultra-wide (billboard).
- **Breakpoints** (`useResponsive` hook on top of `useWindowDimensions`):
  - `mobile`:  `< 600`
  - `tablet`:  `600–959`
  - `desktop`: `960–1439`
  - `wide`:    `≥ 1440`
- **Layout strategy**:
  - Mobile: bottom tab bar, full-width screens.
  - Tablet/desktop/wide: persistent left sidebar nav, top app bar, content area capped at `maxWidth: 1280` and centered, with multi-column grids on desktop+ (stat cards 2-up on mobile, 4-up on desktop).
  - Use flex (and CSS Grid via `display: 'grid'` on web only where it materially helps) — never width: '100%' on stretched cards; cap with `maxWidth`.
- **Typography scale** uses MD3 ramp (see §6). Body sizes do not change across breakpoints; only headlines/displays scale up on `desktop+`.
- **Touch targets** minimum 44×44.

---

## 5. Required Screens

### 5.1 Auth
- **LoginScreen**: email + password, "Forgot?" placeholder (no backend yet — flag in §9), link to Register.
- **RegisterScreen**: email, username, password, password_confirm, optional first/last name. Password strength meter. Auto-login on success.
- **EmailVerificationScreen**: shows current status from `GET /auth/email/status/`. "Resend email" button calls `POST /auth/email/verify/send/`. If route is opened with `?token=&uid=` (deep link from email), POSTs to `/auth/email/verify/confirm/` automatically.

### 5.2 DashboardScreen
- 4 stat cards (responsive grid): **Connected platforms** (count from `/integrations/`), **Active channels** (sum of `channels_count`), **Email verified** (badge), **Account age** (from `date_joined`).
- "Recent connections" list (top 5 from `/integrations/`).
- Coming-soon banner for Summaries.

### 5.3 IntegrationsScreen
- List from `GET /integrations/`. Cards show platform icon, `platform_username`, `status` chip (active/expired/error/revoked), `channels_count`, `last_sync` (`date-fns/formatDistanceToNow`).
- Card actions: **Refresh** (calls `/integrations/<id>/refresh/`), **View channels** (→ IntegrationDetail), **Disconnect** (DELETE with confirm dialog).
- "+ Connect Discord" → opens `authorization_url` in `Linking.openURL`.
- "+ Connect Telegram" → modal with bot-token input; show inline help "Get token from @BotFather".
- If `email_verified=false`, show banner blocking the connect actions.

### 5.4 IntegrationDetailScreen
- Header: connection summary.
- Channels list from the detail response. Filter by `channel_type`. Each row shows `channel_name`, type badge, `member_count`, permission badges (`can_read_messages`, `can_read_history`).

### 5.5 MonitoringScreen, SummariesScreen
- "Coming Soon" empty state: large icon, headline, sub-copy describing the feature, a disabled CTA, and a "Notify me" button that's a no-op (purely visual). **Do not** call any monitoring/summary endpoint.

### 5.6 SettingsScreen
- Edit profile (`PATCH /users/me/`): username, first_name, last_name, profile.timezone (dropdown of common IANA zones), profile.preferred_summary_time (time picker → `"HH:MM:SS"`).
- Sign out → `POST /auth/logout/` then clear storage.
- Delete account → `DELETE /users/me/` with confirm.

---

## 6. Design System (Material Design 3 — locked)

```ts
export const colors = {
  primary: '#6750A4', primaryLight: '#9A82DB', primaryDark: '#4F378B',
  secondary: '#625B71', tertiary: '#7D5260',
  success: '#2E7D32', error: '#B3261E', warning: '#F57C00', info: '#0288D1',
  surface: '#FFFBFE', surfaceVariant: '#E7E0EC', background: '#FFFBFE',
  textPrimary: '#1C1B1F', textSecondary: '#49454F', textTertiary: '#79747E',
  border: '#CAC4D0', divider: '#E7E0EC',
};
export const spacing = { xs:4, sm:8, md:16, lg:24, xl:32, xxl:48 };
export const radius  = { xs:4, sm:8, md:12, lg:16, xl:28, full:9999 };
export const typography = {
  displayLarge:    { fontSize:57, fontWeight:'400', lineHeight:64 },
  displayMedium:   { fontSize:45, fontWeight:'400', lineHeight:52 },
  headlineLarge:   { fontSize:32, fontWeight:'400', lineHeight:40 },
  headlineMedium:  { fontSize:28, fontWeight:'400', lineHeight:36 },
  headlineSmall:   { fontSize:24, fontWeight:'400', lineHeight:32 },
  titleLarge:      { fontSize:22, fontWeight:'500', lineHeight:28 },
  titleMedium:     { fontSize:16, fontWeight:'500', lineHeight:24 },
  titleSmall:      { fontSize:14, fontWeight:'500', lineHeight:20 },
  bodyLarge:       { fontSize:16, fontWeight:'400', lineHeight:24 },
  bodyMedium:      { fontSize:14, fontWeight:'400', lineHeight:20 },
  bodySmall:       { fontSize:12, fontWeight:'400', lineHeight:16 },
  labelLarge:      { fontSize:14, fontWeight:'500', lineHeight:20 },
  labelMedium:     { fontSize:12, fontWeight:'500', lineHeight:16 },
} as const;
```

Wire the Paper theme to use these colors so default Paper components match.

---

## 7. Architecture

- **Functional components + hooks only**, TypeScript strict.
- Folder layout (create exactly):
  ```
  frontend/
  ├── App.tsx                    # QueryClientProvider, PaperProvider, NavigationContainer
  ├── app.json                   # Expo config (scheme: "chatsift")
  ├── package.json
  ├── tsconfig.json              # strict: true
  ├── babel.config.js            # expo preset + reanimated plugin
  └── src/
      ├── api/
      │   ├── client.ts          # axios instance + interceptors
      │   ├── auth.ts
      │   ├── integrations.ts
      │   └── types.ts           # User, PlatformConnection, Channel, paginated<T>
      ├── components/
      │   ├── common/            # Button, Card, Input, Loading, EmptyState, ComingSoon, ErrorBanner
      │   └── layout/            # AppBar, Sidebar, Container, ResponsiveGrid
      ├── screens/
      │   ├── auth/{Login,Register,EmailVerification}Screen.tsx
      │   ├── DashboardScreen.tsx
      │   ├── IntegrationsScreen.tsx
      │   ├── IntegrationDetailScreen.tsx
      │   ├── MonitoringScreen.tsx
      │   ├── SummariesScreen.tsx
      │   └── SettingsScreen.tsx
      ├── navigation/
      │   ├── AppNavigator.tsx
      │   ├── AuthNavigator.tsx
      │   └── MainNavigator.tsx  # tabs on mobile, sidebar layout on tablet+
      ├── store/
      │   ├── authStore.ts       # zustand persist via AsyncStorage
      │   └── uiStore.ts         # snackbar/toast queue
      ├── hooks/
      │   ├── useAuth.ts
      │   ├── useEmailStatus.ts
      │   ├── useIntegrations.ts
      │   └── useResponsive.ts
      ├── theme/theme.ts
      ├── utils/
      │   ├── storage.ts         # AsyncStorage wrapper
      │   ├── validation.ts      # zod schemas
      │   └── errors.ts          # parseDrfError(error) → { fieldErrors, message }
      └── types/index.ts
  ```
- **Centralized API**: every network call goes through `src/api/client.ts`. Screens call hooks; hooks call `api.*`. No `fetch`/`axios` in components.
- **Reusable components** for Button, Card, Input, EmptyState, ComingSoon, ErrorBanner, ResponsiveGrid.

---

## 8. Constraints

- Use the backend exactly as specified in §2. Do not invent endpoints, fields, or query params.
- Do not assume missing fields exist — flag them in §9.
- Do not call monitoring/summaries/notifications endpoints (not wired).
- Code must be minimal but production-quality (typed, no `any` in public APIs, no dead code, no commented-out blocks).
- No extra dependencies beyond §1 without flagging.
- Handle: loading, error, empty, invalid-data, network-down, 401, 403 (email not verified), 404, 5xx.
- Never log or store tokens in plain text outside AsyncStorage. Don't put tokens in URLs.
- Web dev server must run on **port 3000** to satisfy CORS.

---

## OUTPUT (STRICT ORDER — only code blocks + minimal headers, no prose explanations)

1. **Folder structure** (tree).
2. **Global state + API service layer**: `src/api/client.ts`, `src/api/auth.ts`, `src/api/integrations.ts`, `src/api/types.ts`, `src/store/authStore.ts`, `src/store/uiStore.ts`, `src/utils/{storage,validation,errors}.ts`.
3. **Navigation setup**: `App.tsx`, `src/navigation/{App,Auth,Main}Navigator.tsx`, including responsive switch between bottom tabs (mobile) and sidebar layout (tablet+).
4. **Core reusable components**: `src/components/common/{Button,Card,Input,Loading,EmptyState,ComingSoon,ErrorBanner}.tsx`, `src/components/layout/{AppBar,Sidebar,Container,ResponsiveGrid}.tsx`, `src/theme/theme.ts`, `src/hooks/useResponsive.ts`.
5. **Screens with full backend integration**:
   - `src/screens/auth/{Login,Register,EmailVerification}Screen.tsx`
   - `src/screens/DashboardScreen.tsx`
   - `src/screens/IntegrationsScreen.tsx` (incl. Discord OAuth open-URL + Telegram bot-token modal + refresh + disconnect)
   - `src/screens/IntegrationDetailScreen.tsx`
   - `src/screens/MonitoringScreen.tsx` (Coming Soon)
   - `src/screens/SummariesScreen.tsx` (Coming Soon)
   - `src/screens/SettingsScreen.tsx`
   - Hooks: `src/hooks/{useAuth,useEmailStatus,useIntegrations}.ts`
6. **Responsive styling system**: breakpoint constants, `useResponsive`, `ResponsiveGrid` (1/2/3/4-col by breakpoint), max-width container, examples of usage.
7. **Run instructions**:
   - `package.json`, `app.json`, `babel.config.js`, `tsconfig.json`.
   - Commands: `npx create-expo-app chatsift-frontend -t blank-typescript`, `npm install`, `npm run web -- --port 3000`, `npm run ios`, `npm run android`.
   - Notes for iOS/Android extension: `expo prebuild`, native deep-link scheme `chatsift://` for email verification and Discord callback, `app.json` `scheme` field, `Linking` config in `NavigationContainer`.
8. **Missing backend gaps** (must include at minimum):
   - Backend bug: `Infobyte/urls.py` mounts integrations at `api/v1/` instead of `api/v1/integrations/` — frontend assumes the latter; backend must be patched.
   - Discord OAuth callback returns JSON instead of redirecting to a frontend route — needs a proper redirect with deep-link to `chatsift://integrations/discord/callback` (or a web success page) before mobile flow works.
   - `monitoring`, `summaries`, `notifications`, `chats` apps not wired in `urls.py` — all related screens are Coming Soon stubs.
   - No password-reset endpoint despite `PasswordResetRequestSerializer`/`PasswordResetConfirmSerializer` existing — Forgot Password UI is a stub.
   - No "list available channels for monitoring" endpoint exposed — channels are only visible via `GET /integrations/<id>/`.
   - No dashboard/analytics endpoint — Dashboard derives stats client-side from `/integrations/` and `/users/me/`.
   - Unverified-email integration calls return DRF default `403 {"detail":"..."}` rather than the wrapped `{status:"error",...}` envelope — error parser must handle both shapes.
   - Default DRF pagination shape (`{count,next,previous,results}`) is **not** wrapped in `{status,data}` — list endpoints differ from object endpoints; types must reflect that.
   - Email verification uses Django's console backend in dev — verification link prints to backend stdout, not delivered. Document this for graders.

**Output format**: only code blocks + minimal section headers (`## 1. Folder structure`, etc.). No explanations, no commentary, no emoji, no marketing copy. If a constraint cannot be met, stop and list the blocker under §8 instead of fabricating.
