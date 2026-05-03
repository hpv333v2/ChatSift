import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import * as authApi from '../api/auth';
import { storeToken, removeToken } from '../utils/storage';
import { LoginRequest, RegisterRequest } from '../api/types';

export const useAuth = () => {
  const queryClient = useQueryClient();
  const { setAuth, clearAuth, user, isAuthenticated } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: async (response) => {
      const { user, tokens } = response.data;
      
      // Store tokens in secure storage
      await storeToken('access_token', tokens.access);
      await storeToken('refresh_token', tokens.refresh);
      
      // Update auth store
      setAuth(user, tokens.access, tokens.refresh);
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
      queryClient.invalidateQueries({ queryKey: ['emailStatus'] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: async (response) => {
      const { user, tokens } = response.data;
      
      // Store tokens in secure storage
      await storeToken('access_token', tokens.access);
      await storeToken('refresh_token', tokens.refresh);
      
      // Update auth store
      setAuth(user, tokens.access, tokens.refresh);
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
      queryClient.invalidateQueries({ queryKey: ['emailStatus'] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        await authApi.logout({ refresh: refreshToken });
      }
    },
    onSettled: async () => {
      // Clear tokens from secure storage
      await removeToken('access_token');
      await removeToken('refresh_token');
      
      // Clear auth store
      clearAuth();
      
      // Clear all queries
      queryClient.clear();
    },
  });

  return {
    user,
    isAuthenticated,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout: logoutMutation.mutate,
    logoutAsync: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
  };
};

// Made with Bob
