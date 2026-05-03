// Backend contract types from AI_IMPLEMENTATION_PROMPT.md §2.2

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  email_verified: boolean;
  email_verified_at: string | null;
  date_joined: string;
  last_login: string | null;
  profile: {
    timezone: string;
    preferred_summary_time: string; // "HH:MM:SS"
  } | null;
}

export interface AuthTokens {
  refresh: string;
  access: string;
}

export interface ApiResponse<T> {
  status: 'success' | 'error' | 'info';
  data: T;
  message: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export interface RegisterResponse {
  user: User;
  tokens: AuthTokens;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

export interface LogoutRequest {
  refresh: string;
}

export interface RefreshTokenRequest {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
  refresh: string;
}

export interface EmailVerifyConfirmRequest {
  token: string;
  uid: string;
}

export interface EmailVerifyConfirmResponse {
  email_verified: boolean;
  email_verified_at: string;
}

export interface EmailStatusResponse {
  email: string;
  email_verified: boolean;
  email_verified_at: string | null;
  can_create_integrations: boolean;
}

export interface PlatformConnection {
  id: string;
  platform: 'discord' | 'telegram';
  platform_display: 'Discord' | 'Telegram';
  platform_user_id: string;
  platform_username: string;
  status: 'active' | 'expired' | 'revoked' | 'error';
  status_display: string;
  is_token_expired: boolean;
  last_sync: string | null;
  error_message: string | null;
  channels_count: number;
  created_at: string;
  updated_at: string;
}

export interface PlatformConnectionDetail extends PlatformConnection {
  channels: Channel[];
}

export interface Channel {
  id: string;
  channel_id: string;
  channel_name: string;
  channel_type: 'discord_server' | 'discord_channel' | 'telegram_group' | 'telegram_channel';
  platform: 'discord' | 'telegram';
  member_count: number | null;
  icon_url: string | null;
  description: string | null;
  can_read_messages: boolean;
  can_read_history: boolean;
  is_active: boolean;
  last_synced: string | null;
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Made with Bob
