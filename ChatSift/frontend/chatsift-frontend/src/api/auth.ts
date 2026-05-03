import { apiClient } from './client';
import {
  ApiResponse,
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  LoginResponse,
  LogoutRequest,
  EmailVerifyConfirmRequest,
  EmailVerifyConfirmResponse,
  EmailStatusResponse,
  User,
} from './types';

const BASE_PATH = '/api/v1';

export const register = async (data: RegisterRequest) => {
  const response = await apiClient.post<ApiResponse<RegisterResponse>>(
    `${BASE_PATH}/auth/register/`,
    data
  );
  return response.data;
};

export const login = async (data: LoginRequest) => {
  const response = await apiClient.post<ApiResponse<LoginResponse>>(
    `${BASE_PATH}/auth/login/`,
    data
  );
  return response.data;
};

export const logout = async (data: LogoutRequest) => {
  const response = await apiClient.post<ApiResponse<void>>(
    `${BASE_PATH}/auth/logout/`,
    data
  );
  return response.data;
};

export const sendEmailVerification = async () => {
  const response = await apiClient.post<ApiResponse<void>>(
    `${BASE_PATH}/auth/email/verify/send/`
  );
  return response.data;
};

export const confirmEmailVerification = async (data: EmailVerifyConfirmRequest) => {
  const response = await apiClient.post<ApiResponse<EmailVerifyConfirmResponse>>(
    `${BASE_PATH}/auth/email/verify/confirm/`,
    data
  );
  return response.data;
};

export const getEmailStatus = async () => {
  const response = await apiClient.get<ApiResponse<EmailStatusResponse>>(
    `${BASE_PATH}/auth/email/status/`
  );
  return response.data;
};

export const getMe = async () => {
  const response = await apiClient.get<ApiResponse<User>>(
    `${BASE_PATH}/users/me/`
  );
  return response.data;
};

export const updateMe = async (data: Partial<User>) => {
  const response = await apiClient.patch<ApiResponse<User>>(
    `${BASE_PATH}/users/me/`,
    data
  );
  return response.data;
};

export const deleteMe = async () => {
  const response = await apiClient.delete<ApiResponse<void>>(
    `${BASE_PATH}/users/me/`
  );
  return response.data;
};

// Made with Bob
