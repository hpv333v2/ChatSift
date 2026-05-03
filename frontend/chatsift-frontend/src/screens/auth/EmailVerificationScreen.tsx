import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Snackbar, ActivityIndicator } from 'react-native-paper';
import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { useEmailStatus } from '../../hooks/useEmailStatus';
import { parseDrfError } from '../../utils/errors';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors, spacing, typography } from '../../theme/theme';

type EmailVerificationScreenRouteProp = RouteProp<AuthStackParamList, 'EmailVerification'>;
type EmailVerificationScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'EmailVerification'
>;

export function EmailVerificationScreen() {
  const route = useRoute<EmailVerificationScreenRouteProp>();
  const navigation = useNavigation<EmailVerificationScreenNavigationProp>();
  const {
    emailStatus,
    isLoading,
    sendVerification,
    isSendingVerification,
    sendVerificationError,
    confirmVerification,
    isConfirmingVerification,
    confirmVerificationError,
  } = useEmailStatus();

  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [autoVerifyAttempted, setAutoVerifyAttempted] = useState(false);

  // Auto-verify if token and uid are present in route params
  useEffect(() => {
    const { token, uid } = route.params || {};
    
    if (token && uid && !autoVerifyAttempted) {
      setAutoVerifyAttempted(true);
      confirmVerification(
        { token, uid },
        {
          onSuccess: () => {
            setSnackbarMessage('Email verified successfully!');
            setSnackbarVisible(true);
            // Navigate back to login or main app after a delay
            setTimeout(() => {
              navigation.navigate('Login');
            }, 2000);
          },
          onError: (error) => {
            const { message } = parseDrfError(error);
            setSnackbarMessage(message);
            setSnackbarVisible(true);
          },
        }
      );
    }
  }, [route.params, autoVerifyAttempted, confirmVerification, navigation]);

  const handleSendVerification = () => {
    sendVerification(undefined, {
      onSuccess: (response) => {
        setSnackbarMessage(response.message || 'Verification email sent!');
        setSnackbarVisible(true);
      },
      onError: (error) => {
        const { message } = parseDrfError(error);
        setSnackbarMessage(message);
        setSnackbarVisible(true);
      },
    });
  };

  const handleBackToLogin = () => {
    navigation.navigate('Login');
  };

  if (isLoading || isConfirmingVerification) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>
          {isConfirmingVerification ? 'Verifying email...' : 'Loading...'}
        </Text>
      </View>
    );
  }

  const isVerified = emailStatus?.email_verified;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Email Verification</Text>

        <Card style={styles.card}>
          {isVerified ? (
            <>
              <Text style={styles.successIcon}>✓</Text>
              <Text style={styles.statusTitle}>Email Verified</Text>
              <Text style={styles.statusText}>
                Your email address has been verified successfully.
              </Text>
              <Text style={styles.emailText}>{emailStatus?.email}</Text>
              {emailStatus?.email_verified_at && (
                <Text style={styles.dateText}>
                  Verified on {new Date(emailStatus.email_verified_at).toLocaleDateString()}
                </Text>
              )}
              <Button
                mode="contained"
                onPress={handleBackToLogin}
                style={styles.button}
              >
                Continue to Login
              </Button>
            </>
          ) : (
            <>
              <Text style={styles.warningIcon}>⚠</Text>
              <Text style={styles.statusTitle}>Email Not Verified</Text>
              <Text style={styles.statusText}>
                Please verify your email address to access all features.
              </Text>
              <Text style={styles.emailText}>{emailStatus?.email}</Text>
              <Text style={styles.helperText}>
                Check your inbox for a verification link. If you didn't receive it, you can
                request a new one.
              </Text>
              <Button
                mode="contained"
                onPress={handleSendVerification}
                loading={isSendingVerification}
                disabled={isSendingVerification}
                style={styles.button}
              >
                Send Verification Email
              </Button>
              <Button
                mode="text"
                onPress={handleBackToLogin}
                disabled={isSendingVerification}
                style={styles.secondaryButton}
              >
                Back to Login
              </Button>
            </>
          )}
        </Card>

        {!isVerified && emailStatus?.can_create_integrations === false && (
          <Card style={styles.infoCard}>
            <Text style={styles.infoTitle}>Why verify?</Text>
            <Text style={styles.infoText}>
              • Connect Discord and Telegram integrations{'\n'}
              • Receive daily AI-powered summaries{'\n'}
              • Access all ChatSift features
            </Text>
          </Card>
        )}
      </View>

      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={4000}
        action={{
          label: 'Dismiss',
          onPress: () => setSnackbarVisible(false),
        }}
      >
        {snackbarMessage}
      </Snackbar>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    ...typography.bodyLarge,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  content: {
    maxWidth: 500,
    width: '100%',
    alignSelf: 'center',
  },
  title: {
    ...typography.headlineLarge,
    color: colors.textPrimary,
    marginBottom: spacing.xl,
    textAlign: 'center',
  },
  card: {
    padding: spacing.xl,
    alignItems: 'center',
  },
  successIcon: {
    fontSize: 64,
    color: colors.success,
    marginBottom: spacing.md,
  },
  warningIcon: {
    fontSize: 64,
    color: colors.warning,
    marginBottom: spacing.md,
  },
  statusTitle: {
    ...typography.headlineMedium,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  statusText: {
    ...typography.bodyLarge,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  emailText: {
    ...typography.titleMedium,
    color: colors.primary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  dateText: {
    ...typography.bodySmall,
    color: colors.textTertiary,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  helperText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    textAlign: 'center',
    lineHeight: 20,
  },
  button: {
    width: '100%',
    marginTop: spacing.md,
  },
  secondaryButton: {
    marginTop: spacing.sm,
  },
  infoCard: {
    marginTop: spacing.lg,
    padding: spacing.lg,
    backgroundColor: colors.surfaceVariant,
  },
  infoTitle: {
    ...typography.titleMedium,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  infoText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    lineHeight: 24,
  },
});

// Made with Bob