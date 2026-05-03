import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert, Platform } from 'react-native';
import { Text, Portal, Dialog, Button as PaperButton } from 'react-native-paper';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Container } from '../components/layout/Container';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { useAuthStore } from '../store/authStore';
import { useUiStore } from '../store/uiStore';
import { getMe, updateMe, deleteMe, logout } from '../api/auth';
import { spacing, colors } from '../theme/theme';
import { User } from '../api/types';

// Common IANA timezones
const TIMEZONES = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Toronto',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Kolkata',
  'Asia/Dubai',
  'Australia/Sydney',
  'Pacific/Auckland',
];

// Validation schema
const profileSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  timezone: z.string().min(1, 'Timezone is required'),
  preferred_summary_time: z.string().regex(/^\d{2}:\d{2}:\d{2}$/, 'Time must be in HH:MM:SS format'),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function SettingsScreen() {
  const { user, clearAuth, refreshToken, updateUser } = useAuthStore();
  const showSnackbar = useUiStore((state) => state.showSnackbar);
  const queryClient = useQueryClient();
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  const [signOutDialogVisible, setSignOutDialogVisible] = useState(false);

  // Fetch user data
  const { data: userData, isLoading, error, refetch } = useQuery({
    queryKey: ['user', 'me'],
    queryFn: getMe,
    staleTime: 60_000,
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: '',
      first_name: '',
      last_name: '',
      timezone: 'UTC',
      preferred_summary_time: '09:00:00',
    },
  });

  // Update form when user data loads
  useEffect(() => {
    if (userData?.data) {
      const user = userData.data;
      reset({
        username: user.username,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        timezone: user.profile?.timezone || 'UTC',
        preferred_summary_time: user.profile?.preferred_summary_time || '09:00:00',
      });
    }
  }, [userData, reset]);

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: ProfileFormData) => {
      return updateMe({
        username: data.username,
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        profile: {
          timezone: data.timezone,
          preferred_summary_time: data.preferred_summary_time,
        },
      });
    },
    onSuccess: (response) => {
      showSnackbar(response.message || 'Profile updated successfully', 'success');
      updateUser(response.data);
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
      reset({
        username: response.data.username,
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        timezone: response.data.profile?.timezone || 'UTC',
        preferred_summary_time: response.data.profile?.preferred_summary_time || '09:00:00',
      });
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Failed to update profile';
      showSnackbar(message, 'error');
    },
  });

  // Sign out mutation
  const signOutMutation = useMutation({
    mutationFn: () => logout({ refresh: refreshToken || '' }),
    onSuccess: () => {
      clearAuth();
      showSnackbar('Signed out successfully', 'success');
    },
    onError: (error: any) => {
      // Still clear auth even if logout fails
      clearAuth();
      const message = error.response?.data?.message || 'Signed out';
      showSnackbar(message, 'info');
    },
  });

  // Delete account mutation
  const deleteAccountMutation = useMutation({
    mutationFn: deleteMe,
    onSuccess: (response) => {
      clearAuth();
      showSnackbar(response.message || 'Account deleted successfully', 'success');
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Failed to delete account';
      showSnackbar(message, 'error');
    },
  });

  const onSubmit = (data: ProfileFormData) => {
    updateProfileMutation.mutate(data);
  };

  const handleSignOut = () => {
    setSignOutDialogVisible(true);
  };

  const confirmSignOut = () => {
    setSignOutDialogVisible(false);
    signOutMutation.mutate();
  };

  const handleDeleteAccount = () => {
    setDeleteDialogVisible(true);
  };

  const confirmDeleteAccount = () => {
    setDeleteDialogVisible(false);
    deleteAccountMutation.mutate();
  };

  if (isLoading) {
    return <Loading />;
  }

  if (error) {
    return (
      <Container>
        <ErrorBanner
          message="Failed to load settings"
          onRetry={refetch}
        />
      </Container>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Container maxWidth={800}>
        <Text variant="headlineMedium" style={styles.title}>
          Settings
        </Text>

        <Card style={styles.card}>
          <Text variant="titleLarge" style={styles.sectionTitle}>
            Profile Information
          </Text>

          <Controller
            control={control}
            name="username"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                label="Username"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={!!errors.username}
                style={styles.input}
              />
            )}
          />
          {errors.username && (
            <Text style={styles.errorText}>{errors.username.message}</Text>
          )}

          <Controller
            control={control}
            name="first_name"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                label="First Name (Optional)"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                style={styles.input}
              />
            )}
          />

          <Controller
            control={control}
            name="last_name"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                label="Last Name (Optional)"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                style={styles.input}
              />
            )}
          />

          <Controller
            control={control}
            name="timezone"
            render={({ field: { onChange, value } }) => (
              <View style={styles.input}>
                <Text variant="bodySmall" style={styles.label}>
                  Timezone
                </Text>
                <View style={styles.pickerContainer}>
                  {TIMEZONES.map((tz) => (
                    <PaperButton
                      key={tz}
                      mode={value === tz ? 'contained' : 'outlined'}
                      onPress={() => onChange(tz)}
                      style={styles.timezoneButton}
                      compact
                    >
                      {tz}
                    </PaperButton>
                  ))}
                </View>
              </View>
            )}
          />
          {errors.timezone && (
            <Text style={styles.errorText}>{errors.timezone.message}</Text>
          )}

          <Controller
            control={control}
            name="preferred_summary_time"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                label="Preferred Summary Time (HH:MM:SS)"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={!!errors.preferred_summary_time}
                placeholder="09:00:00"
                style={styles.input}
              />
            )}
          />
          {errors.preferred_summary_time && (
            <Text style={styles.errorText}>
              {errors.preferred_summary_time.message}
            </Text>
          )}

          <Button
            mode="contained"
            onPress={handleSubmit(onSubmit)}
            loading={updateProfileMutation.isPending}
            disabled={!isDirty || updateProfileMutation.isPending}
            style={styles.button}
          >
            Save Changes
          </Button>
        </Card>

        <Card style={styles.card}>
          <Text variant="titleLarge" style={styles.sectionTitle}>
            Account Actions
          </Text>

          <Button
            mode="outlined"
            onPress={handleSignOut}
            loading={signOutMutation.isPending}
            disabled={signOutMutation.isPending}
            style={styles.button}
          >
            Sign Out
          </Button>

          <Button
            mode="contained"
            onPress={handleDeleteAccount}
            loading={deleteAccountMutation.isPending}
            disabled={deleteAccountMutation.isPending}
            buttonColor={colors.error}
            style={styles.button}
          >
            Delete Account
          </Button>
        </Card>
      </Container>

      {/* Sign Out Confirmation Dialog */}
      <Portal>
        <Dialog
          visible={signOutDialogVisible}
          onDismiss={() => setSignOutDialogVisible(false)}
        >
          <Dialog.Title>Sign Out</Dialog.Title>
          <Dialog.Content>
            <Text>Are you sure you want to sign out?</Text>
          </Dialog.Content>
          <Dialog.Actions>
            <PaperButton onPress={() => setSignOutDialogVisible(false)}>
              Cancel
            </PaperButton>
            <PaperButton onPress={confirmSignOut}>Sign Out</PaperButton>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      {/* Delete Account Confirmation Dialog */}
      <Portal>
        <Dialog
          visible={deleteDialogVisible}
          onDismiss={() => setDeleteDialogVisible(false)}
        >
          <Dialog.Title>Delete Account</Dialog.Title>
          <Dialog.Content>
            <Text>
              Are you sure you want to delete your account? This action cannot be undone.
            </Text>
          </Dialog.Content>
          <Dialog.Actions>
            <PaperButton onPress={() => setDeleteDialogVisible(false)}>
              Cancel
            </PaperButton>
            <PaperButton
              onPress={confirmDeleteAccount}
              textColor={colors.error}
            >
              Delete
            </PaperButton>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  title: {
    marginTop: spacing.lg,
    marginBottom: spacing.md,
    color: colors.textPrimary,
  },
  card: {
    marginBottom: spacing.md,
  },
  sectionTitle: {
    marginBottom: spacing.md,
    color: colors.textPrimary,
  },
  input: {
    marginBottom: spacing.md,
  },
  label: {
    marginBottom: spacing.xs,
    color: colors.textSecondary,
  },
  pickerContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  timezoneButton: {
    marginBottom: spacing.xs,
  },
  button: {
    marginTop: spacing.sm,
  },
  errorText: {
    color: colors.error,
    fontSize: 12,
    marginTop: -spacing.sm,
    marginBottom: spacing.sm,
  },
});

// Made with Bob