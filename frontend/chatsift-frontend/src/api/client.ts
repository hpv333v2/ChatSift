import axios from 'axios';
import { getToken, storeToken, removeToken } from '../utils/storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await getToken('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await getToken('refresh_token');
        
        if (!refreshToken) {
          // No refresh token, redirect to login
          await removeToken('access_token');
          await removeToken('refresh_token');
          // Navigation to login will be handled by the app
          return Promise.reject(error);
        }

        // Call refresh endpoint
        const response = await apiClient.post('/api/v1/auth/refresh/', {
          refresh: refreshToken,
        });

        const { access, refresh } = response.data;

        // Store new tokens
        await storeToken('access_token', access);
        await storeToken('refresh_token', refresh);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        await removeToken('access_token');
        await removeToken('refresh_token');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Made with Bob
