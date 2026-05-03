import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, Linking, RefreshControl } from 'react-native';
import { Icon, Portal, Modal, TextInput as PaperInput } from 'react-native-paper';
import { formatDistanceToNow } from 'date-fns';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useIntegrations, useDeleteIntegration, useRefreshIntegration, useDiscordAuthUrl, useConnectTelegram } from '../hooks/useIntegrations';
import { useEmailStatus } from '../hooks/useEmailStatus';
import { useUiStore } from '../store/uiStore';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Loading } from '../components/common/Loading';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { EmptyState } from '../components/common/EmptyState';
import { Container } from '../components/layout/Container';
import { ResponsiveGrid } from '../components/layout/ResponsiveGrid';
import { colors, spacing, typography } from '../theme/theme';
import type { PlatformConnection } from '../api/types';
import type { MainTabParamList } from '../navigation/MainNavigator';
import { z } from 'zod';

// Telegram bot token validation schema
const telegramTokenSchema = z.string().regex(/^\d+:[\w-]{30,}$/, 'Invalid bot token format');

type NavigationProp = NativeStackNavigationProp<MainTabParamList, 'Integrations'>;

export function IntegrationsScreen() {
  const navigation = useNavigation<NavigationProp>();
  const showSnackbar = useUiStore((state) => state.showSnackbar);
  const [telegramModalVisible, setTelegramModalVisible] = useState(false);
  const [telegramToken, setTelegramToken] = useState('');
  const [telegramError, setTelegramError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const { data: integrations, isLoading, error, refetch } = useIntegrations();
  const { emailStatus } = useEmailStatus();
  const deleteIntegration = useDeleteIntegration();
  const refreshIntegration = useRefreshIntegration();
  const discordAuthUrl = useDiscordAuthUrl();
  const connectTelegram = useConnectTelegram();

  const emailVerified = emailStatus?.email_verified ?? false;

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleConnectDiscord = async () => {
    if (!emailVerified) {
      Alert.alert('Email Not Verified', 'Please verify your email before connecting integrations.');
      return;
    }

    try {
      const url = await discordAuthUrl.mutateAsync();
      await Linking.openURL(url);
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Failed to get Discord authorization URL');
    }
  };

  const handleConnectTelegram = () => {
    if (!emailVerified) {
      Alert.alert('Email Not Verified', 'Please verify your email before connecting integrations.');
      return;
    }
    setTelegramModalVisible(true);
    setTelegramToken('');
    setTelegramError('');
  };

  const handleTelegramSubmit = async () => {
    setTelegramError('');

    // Validate token
    const validation = telegramTokenSchema.safeParse(telegramToken);
    if (!validation.success) {
      setTelegramError('Invalid bot token format. Expected format: 123456:ABC-...');
      return;
    }

    try {
      await connectTelegram.mutateAsync(telegramToken);
      setTelegramModalVisible(false);
      setTelegramToken('');
      showSnackbar('Telegram bot connected successfully!', 'success');
    } catch (err: any) {
      setTelegramError(err.message || 'Failed to connect Telegram bot');
    }
  };

  const handleRefresh = async (id: string) => {
    try {
      await refreshIntegration.mutateAsync(id);
      showSnackbar('Connection refreshed successfully!', 'success');
    } catch (err: any) {
      showSnackbar(err.message || 'Failed to refresh connection', 'error');
    }
  };

  const handleDisconnect = (connection: PlatformConnection) => {
    Alert.alert(
      'Disconnect Platform',
      `Are you sure you want to disconnect ${connection.platform_display}? This will remove all associated channels.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disconnect',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteIntegration.mutateAsync(connection.id);
              showSnackbar('Platform disconnected successfully', 'success');
            } catch (err: any) {
              showSnackbar(err.message || 'Failed to disconnect platform', 'error');
            }
          },
        },
      ]
    );
  };

  if (isLoading) {
    return <Loading />;
  }

  if (error) {
    return (
      <Container>
        <ErrorBanner message={error.message} />
      </Container>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />
      }
    >
      <Container>
        <Text style={styles.title}>Integrations</Text>

        {/* Email Verification Banner */}
        {!emailVerified && (
          <ErrorBanner
            message="Please verify your email to connect platforms"
            style={styles.banner}
          />
        )}

        {/* Connect Buttons */}
        <ResponsiveGrid columns={{ mobile: 1, tablet: 2, desktop: 2 }}>
          <Button
            mode="contained"
            onPress={handleConnectDiscord}
            disabled={!emailVerified || discordAuthUrl.isPending}
            icon="discord"
            style={styles.connectButton}
          >
            Connect Discord
          </Button>
          <Button
            mode="contained"
            onPress={handleConnectTelegram}
            disabled={!emailVerified || connectTelegram.isPending}
            icon="telegram"
            style={styles.connectButton}
          >
            Connect Telegram
          </Button>
        </ResponsiveGrid>

        {/* Integrations List */}
        {!integrations || integrations.length === 0 ? (
          <EmptyState
            icon="connection"
            title="No Integrations"
            message="Connect Discord or Telegram to start monitoring your group chats"
          />
        ) : (
          <View style={styles.list}>
            {integrations.map((connection: PlatformConnection) => (
              <Card key={connection.id}>
                <Card.Content style={styles.connectionCard}>
                  <View style={styles.connectionHeader}>
                    <Icon
                      source={connection.platform === 'discord' ? 'discord' : 'telegram'}
                      size={32}
                      color={colors.primary}
                    />
                    <View style={styles.connectionInfo}>
                      <Text style={styles.connectionPlatform}>{connection.platform_display}</Text>
                      <Text style={styles.connectionUsername}>{connection.platform_username}</Text>
                    </View>
                    <View style={[styles.statusBadge, getStatusBadgeStyle(connection.status)]}>
                      <Text style={styles.statusText}>{connection.status_display}</Text>
                    </View>
                  </View>

                  <View style={styles.connectionMeta}>
                    <View style={styles.metaItem}>
                      <Icon source="forum" size={16} color={colors.textSecondary} />
                      <Text style={styles.metaText}>
                        {connection.channels_count} {connection.channels_count === 1 ? 'channel' : 'channels'}
                      </Text>
                    </View>
                    {connection.last_sync && (
                      <View style={styles.metaItem}>
                        <Icon source="sync" size={16} color={colors.textSecondary} />
                        <Text style={styles.metaText}>
                          {formatDistanceToNow(new Date(connection.last_sync), { addSuffix: true })}
                        </Text>
                      </View>
                    )}
                  </View>

                  {connection.error_message && (
                    <View style={styles.errorContainer}>
                      <Icon source="alert-circle" size={16} color={colors.error} />
                      <Text style={styles.errorText}>{connection.error_message}</Text>
                    </View>
                  )}

                  <View style={styles.actions}>
                    <Button
                      mode="outlined"
                      onPress={() => handleRefresh(connection.id)}
                      disabled={refreshIntegration.isPending}
                      compact
                    >
                      Refresh
                    </Button>
                    <Button
                      mode="outlined"
                      onPress={() => navigation.navigate('IntegrationDetail', { id: connection.id })}
                      compact
                    >
                      View Channels
                    </Button>
                    <Button
                      mode="outlined"
                      onPress={() => handleDisconnect(connection)}
                      disabled={deleteIntegration.isPending}
                      textColor={colors.error}
                      compact
                    >
                      Disconnect
                    </Button>
                  </View>
                </Card.Content>
              </Card>
            ))}
          </View>
        )}

        {/* Telegram Modal */}
        <Portal>
          <Modal
            visible={telegramModalVisible}
            onDismiss={() => setTelegramModalVisible(false)}
            contentContainerStyle={styles.modal}
          >
            <Text style={styles.modalTitle}>Connect Telegram Bot</Text>
            <Text style={styles.modalDescription}>
              Get your bot token from @BotFather on Telegram
            </Text>

            <PaperInput
              label="Bot Token"
              value={telegramToken}
              onChangeText={setTelegramToken}
              placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
              mode="outlined"
              error={!!telegramError}
              style={styles.input}
            />
            {telegramError && <Text style={styles.inputError}>{telegramError}</Text>}

            <View style={styles.modalActions}>
              <Button
                mode="outlined"
                onPress={() => setTelegramModalVisible(false)}
                style={styles.modalButton}
              >
                Cancel
              </Button>
              <Button
                mode="contained"
                onPress={handleTelegramSubmit}
                loading={connectTelegram.isPending}
                disabled={!telegramToken || connectTelegram.isPending}
                style={styles.modalButton}
              >
                Connect
              </Button>
            </View>
          </Modal>
        </Portal>
      </Container>
    </ScrollView>
  );
}

function getStatusBadgeStyle(status: string) {
  switch (status) {
    case 'active':
      return { backgroundColor: colors.success + '20', borderColor: colors.success };
    case 'expired':
      return { backgroundColor: colors.warning + '20', borderColor: colors.warning };
    case 'error':
    case 'revoked':
      return { backgroundColor: colors.error + '20', borderColor: colors.error };
    default:
      return { backgroundColor: colors.surfaceVariant, borderColor: colors.border };
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  title: {
    ...typography.headlineLarge,
    color: colors.textPrimary,
    marginBottom: spacing.lg,
  },
  banner: {
    marginBottom: spacing.lg,
  },
  connectButton: {
    marginBottom: spacing.md,
  },
  list: {
    marginTop: spacing.xl,
  },
  connectionCard: {
    padding: spacing.md,
  },
  connectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  connectionInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  connectionPlatform: {
    ...typography.titleLarge,
    color: colors.textPrimary,
  },
  connectionUsername: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    borderWidth: 1,
  },
  statusText: {
    ...typography.labelMedium,
    fontSize: 11,
    color: colors.textPrimary,
    textTransform: 'capitalize',
  },
  connectionMeta: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  metaText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    padding: spacing.sm,
    backgroundColor: colors.error + '10',
    borderRadius: spacing.xs,
    marginBottom: spacing.md,
  },
  errorText: {
    ...typography.bodySmall,
    color: colors.error,
    flex: 1,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.sm,
    flexWrap: 'wrap',
  },
  modal: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    margin: spacing.xl,
    borderRadius: spacing.md,
  },
  modalTitle: {
    ...typography.headlineSmall,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  modalDescription: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  input: {
    marginBottom: spacing.xs,
  },
  inputError: {
    ...typography.bodySmall,
    color: colors.error,
    marginBottom: spacing.md,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  modalButton: {
    minWidth: 100,
  },
});

// Made with Bob