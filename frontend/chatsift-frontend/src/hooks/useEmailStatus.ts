import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as authApi from '../api/auth';
import { EmailVerifyConfirmRequest } from '../api/types';

export const useEmailStatus = () => {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['emailStatus'],
    queryFn: authApi.getEmailStatus,
    staleTime: 60_000, // 1 minute
  });

  const sendVerificationMutation = useMutation({
    mutationFn: authApi.sendEmailVerification,
    onSuccess: () => {
      // Optionally refetch status after sending
      queryClient.invalidateQueries({ queryKey: ['emailStatus'] });
    },
  });

  const confirmVerificationMutation = useMutation({
    mutationFn: (data: EmailVerifyConfirmRequest) => 
      authApi.confirmEmailVerification(data),
    onSuccess: () => {
      // Refetch email status and user data
      queryClient.invalidateQueries({ queryKey: ['emailStatus'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
    },
  });

  return {
    emailStatus: data?.data,
    isLoading,
    error,
    refetch,
    sendVerification: sendVerificationMutation.mutate,
    sendVerificationAsync: sendVerificationMutation.mutateAsync,
    isSendingVerification: sendVerificationMutation.isPending,
    sendVerificationError: sendVerificationMutation.error,
    confirmVerification: confirmVerificationMutation.mutate,
    confirmVerificationAsync: confirmVerificationMutation.mutateAsync,
    isConfirmingVerification: confirmVerificationMutation.isPending,
    confirmVerificationError: confirmVerificationMutation.error,
  };
};

// Made with Bob