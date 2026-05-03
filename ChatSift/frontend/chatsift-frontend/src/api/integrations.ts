import { apiClient } from './client';
import type { PlatformConnection, PlatformConnectionDetail, ApiResponse } from './types';

const BASE_PATH = '/api/v1/integrations';

// GET /integrations/ - List all connections
export const getIntegrations = async (): Promise<PlatformConnection[]> => {
  const response = await apiClient.get<ApiResponse<{ connections: PlatformConnection[] }>>(`${BASE_PATH}/`);
  return response.data.data.connections;
};

// GET /integrations/<uuid:id>/ - Get connection detail with channels
export const getIntegrationDetail = async (id: string): Promise<PlatformConnectionDetail> => {
  const response = await apiClient.get<ApiResponse<PlatformConnectionDetail>>(`${BASE_PATH}/${id}/`);
  return response.data.data;
};

// DELETE /integrations/<uuid:id>/ - Disconnect platform
export const deleteIntegration = async (id: string): Promise<void> => {
  await apiClient.delete(`${BASE_PATH}/${id}/`);
};

// POST /integrations/<uuid:id>/refresh/ - Refresh connection and sync channels
export const refreshIntegration = async (id: string): Promise<{
  channels_synced: number;
  channels_added: number;
  channels_removed: number;
  last_sync: string;
}> => {
  const response = await apiClient.post<ApiResponse<{
    channels_synced: number;
    channels_added: number;
    channels_removed: number;
    last_sync: string;
  }>>(`${BASE_PATH}/${id}/refresh/`);
  return response.data.data;
};

// GET /integrations/discord/authorize/ - Get Discord OAuth URL
export const getDiscordAuthUrl = async (): Promise<string> => {
  const response = await apiClient.get<ApiResponse<{ authorization_url: string }>>(`${BASE_PATH}/discord/authorize/`);
  return response.data.data.authorization_url;
};

// POST /integrations/telegram/connect/ - Connect Telegram bot
export const connectTelegram = async (botToken: string): Promise<PlatformConnection> => {
  const response = await apiClient.post<ApiResponse<PlatformConnection>>(`${BASE_PATH}/telegram/connect/`, {
    bot_token: botToken,
  });
  return response.data.data;
};

// Made with Bob
