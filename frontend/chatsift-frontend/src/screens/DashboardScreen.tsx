import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Icon } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { useIntegrations } from '../hooks/useIntegrations';
import { useAuthStore } from '../store/authStore';
import { getMe } from '../api/auth';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { Container } from '../components/layout/Container';
import { ResponsiveGrid } from '../components/layout/ResponsiveGrid';
import { colors, spacing, typography } from '../theme/theme';
import type { User, PlatformConnection } from '../api/types';

export function DashboardScreen() {
  const { user: storeUser } = useAuthStore();
  const [refreshing, setRefreshing] = useState(false);
  
  // Fetch user data
  const { data: userResponse, isLoading: userLoading, error: userError, refetch: refetchUser } = useQuery({
    queryKey: ['user', 'me'],
    queryFn: getMe,
  });

  // Fetch integrations
  const { data: integrations, isLoading: integrationsLoading, error: integrationsError, refetch: refetchIntegrations } = useIntegrations();

  const isLoading = userLoading || integrationsLoading;
  const error = userError || integrationsError;

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchUser(), refetchIntegrations()]);
    setRefreshing(false);
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

  const user = userResponse?.data || storeUser;
  if (!user) {
    return (
      <Container>
        <ErrorBanner message="User data not available" />
      </Container>
    );
  }

  // Calculate stats
  const connectedPlatforms = integrations?.length || 0;
  const activeChannels = integrations?.reduce((sum: number, conn: PlatformConnection) => sum + conn.channels_count, 0) || 0;
  const emailVerified = user.email_verified;
  const accountAge = user.date_joined ? formatDistanceToNow(new Date(user.date_joined), { addSuffix: true }) : 'Unknown';

  // Recent connections (top 5, sorted by created_at desc)
  const recentConnections = integrations
    ?.slice()
    .sort((a: PlatformConnection, b: PlatformConnection) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5) || [];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />
      }
    >
      <Container>
        <Text style={styles.title}>Dashboard</Text>
        
        {/* Stat Cards */}
        <ResponsiveGrid columns={{ mobile: 2, tablet: 2, desktop: 4 }}>
          <StatCard
            icon="connection"
            label="Connected Platforms"
            value={connectedPlatforms.toString()}
            color={colors.primary}
          />
          <StatCard
            icon="forum"
            label="Active Channels"
            value={activeChannels.toString()}
            color={colors.secondary}
          />
          <StatCard
            icon={emailVerified ? 'check-circle' : 'alert-circle'}
            label="Email Status"
            value={emailVerified ? 'Verified' : 'Not Verified'}
            color={emailVerified ? colors.success : colors.warning}
          />
          <StatCard
            icon="calendar"
            label="Account Age"
            value={accountAge}
            color={colors.info}
          />
        </ResponsiveGrid>

        {/* Recent Connections */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Connections</Text>
          {recentConnections.length === 0 ? (
            <Card>
              <Card.Content style={styles.emptyCard}>
                <Text style={styles.emptyText}>No connections yet. Connect Discord or Telegram to get started!</Text>
              </Card.Content>
            </Card>
          ) : (
            recentConnections.map((connection: PlatformConnection) => (
              <Card key={connection.id}>
                <Card.Content style={styles.connectionCard}>
                  <View style={styles.connectionHeader}>
                    <Icon
                      source={connection.platform === 'discord' ? 'discord' : 'telegram'}
                      size={24}
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
                    <Text style={styles.metaText}>
                      {connection.channels_count} {connection.channels_count === 1 ? 'channel' : 'channels'}
                    </Text>
                    <Text style={styles.metaText}>•</Text>
                    <Text style={styles.metaText}>
                      {connection.last_sync
                        ? `Synced ${formatDistanceToNow(new Date(connection.last_sync), { addSuffix: true })}`
                        : 'Not synced yet'}
                    </Text>
                  </View>
                </Card.Content>
              </Card>
            ))
          )}
        </View>

        {/* Coming Soon Banner */}
        <Card>
          <Card.Content style={styles.comingSoonCard}>
            <Icon source="file-document" size={48} color={colors.primary} />
            <Text style={styles.comingSoonTitle}>AI Summaries Coming Soon</Text>
            <Text style={styles.comingSoonText}>
              Daily AI-powered summaries of your group chats will be available soon!
            </Text>
          </Card.Content>
        </Card>
      </Container>
    </ScrollView>
  );
}

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
  color: string;
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <Card>
      <Card.Content style={styles.statCard}>
        <Icon source={icon} size={32} color={color} />
        <Text style={styles.statValue}>{value}</Text>
        <Text style={styles.statLabel}>{label}</Text>
      </Card.Content>
    </Card>
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
  section: {
    marginTop: spacing.xl,
  },
  sectionTitle: {
    ...typography.titleLarge,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  statCard: {
    alignItems: 'center',
    padding: spacing.lg,
    minHeight: 140,
    justifyContent: 'center',
  },
  statValue: {
    ...typography.headlineMedium,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  statLabel: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
  emptyCard: {
    padding: spacing.lg,
    alignItems: 'center',
  },
  emptyText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  connectionCard: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  connectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  connectionInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  connectionPlatform: {
    ...typography.titleMedium,
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
    alignItems: 'center',
    gap: spacing.sm,
  },
  metaText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  comingSoonCard: {
    padding: spacing.xl,
    alignItems: 'center',
    marginTop: spacing.xl,
    marginBottom: spacing.xl,
  },
  comingSoonTitle: {
    ...typography.titleLarge,
    color: colors.textPrimary,
    marginTop: spacing.md,
    textAlign: 'center',
  },
  comingSoonText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
});

// Made with Bob