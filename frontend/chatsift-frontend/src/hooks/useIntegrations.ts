import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as integrationsApi from '../api/integrations';
import type { PlatformConnection, PlatformConnectionDetail } from '../api/types';

// Query keys
export const integrationsKeys = {
  all: ['integrations'] as const,
  detail: (id: string) => ['integration', id] as const,
};

// Get all integrations
export const useIntegrations = () => {
  return useQuery<PlatformConnection[], Error>({
    queryKey: integrationsKeys.all,
    queryFn: integrationsApi.getIntegrations,
  });
};

// Get integration detail
export const useIntegrationDetail = (id: string) => {
  return useQuery<PlatformConnectionDetail, Error>({
    queryKey: integrationsKeys.detail(id),
    queryFn: () => integrationsApi.getIntegrationDetail(id),
    enabled: !!id,
  });
};

// Delete integration
export const useDeleteIntegration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: integrationsApi.deleteIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: integrationsKeys.all });
    },
  });
};

// Refresh integration
export const useRefreshIntegration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: integrationsApi.refreshIntegration,
    onSuccess: (_data: unknown, id: string) => {
      queryClient.invalidateQueries({ queryKey: integrationsKeys.all });
      queryClient.invalidateQueries({ queryKey: integrationsKeys.detail(id) });
    },
  });
};

// Get Discord authorization URL
export const useDiscordAuthUrl = () => {
  return useMutation({
    mutationFn: integrationsApi.getDiscordAuthUrl,
  });
};

// Connect Telegram
export const useConnectTelegram = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: integrationsApi.connectTelegram,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: integrationsKeys.all });
    },
  });
};

// Made with Bob