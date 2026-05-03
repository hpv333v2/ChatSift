import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList, RefreshControl } from 'react-native';
import { Icon, Chip, SegmentedButtons } from 'react-native-paper';
import { formatDistanceToNow } from 'date-fns';
import { useIntegrationDetail } from '../hooks/useIntegrations';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { EmptyState } from '../components/common/EmptyState';
import { Container } from '../components/layout/Container';
import { colors, spacing, typography } from '../theme/theme';
import type { Channel } from '../api/types';

interface IntegrationDetailScreenProps {
  route: {
    params: {
      id: string;
    };
  };
}

type ChannelTypeFilter = 'all' | 'discord_server' | 'discord_channel' | 'telegram_group' | 'telegram_channel';

export function IntegrationDetailScreen({ route }: IntegrationDetailScreenProps) {
  const { id } = route.params;
  const [channelTypeFilter, setChannelTypeFilter] = useState<ChannelTypeFilter>('all');
  const [refreshing, setRefreshing] = useState(false);

  const { data: integration, isLoading, error, refetch } = useIntegrationDetail(id);

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
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

  if (!integration) {
    return (
      <Container>
        <ErrorBanner message="Integration not found" />
      </Container>
    );
  }

  // Filter channels by type
  const filteredChannels = integration.channels?.filter((channel: Channel) => {
    if (channelTypeFilter === 'all') return true;
    return channel.channel_type === channelTypeFilter;
  }) || [];

  // Get available channel types for this integration
  const availableTypes = new Set(integration.channels?.map((c: Channel) => c.channel_type) || []);
  const filterOptions = [
    { value: 'all', label: 'All' },
    ...(availableTypes.has('discord_server') ? [{ value: 'discord_server', label: 'Servers' }] : []),
    ...(availableTypes.has('discord_channel') ? [{ value: 'discord_channel', label: 'Channels' }] : []),
    ...(availableTypes.has('telegram_group') ? [{ value: 'telegram_group', label: 'Groups' }] : []),
    ...(availableTypes.has('telegram_channel') ? [{ value: 'telegram_channel', label: 'Channels' }] : []),
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />
      }
    >
      <Container>
        {/* Connection Header */}
        <Card>
          <Card.Content style={styles.header}>
            <View style={styles.headerTop}>
              <Icon
                source={integration.platform === 'discord' ? 'discord' : 'telegram'}
                size={48}
                color={colors.primary}
              />
              <View style={styles.headerInfo}>
                <Text style={styles.platform}>{integration.platform_display}</Text>
                <Text style={styles.username}>{integration.platform_username}</Text>
              </View>
              <View style={[styles.statusBadge, getStatusBadgeStyle(integration.status)]}>
                <Text style={styles.statusText}>{integration.status_display}</Text>
              </View>
            </View>

            <View style={styles.headerMeta}>
              <View style={styles.metaItem}>
                <Icon source="forum" size={20} color={colors.textSecondary} />
                <Text style={styles.metaText}>
                  {integration.channels_count} {integration.channels_count === 1 ? 'channel' : 'channels'}
                </Text>
              </View>
              {integration.last_sync && (
                <View style={styles.metaItem}>
                  <Icon source="sync" size={20} color={colors.textSecondary} />
                  <Text style={styles.metaText}>
                    Last synced {formatDistanceToNow(new Date(integration.last_sync), { addSuffix: true })}
                  </Text>
                </View>
              )}
            </View>

            {integration.error_message && (
              <View style={styles.errorContainer}>
                <Icon source="alert-circle" size={16} color={colors.error} />
                <Text style={styles.errorText}>{integration.error_message}</Text>
              </View>
            )}
          </Card.Content>
        </Card>

        {/* Channel Type Filter */}
        {filterOptions.length > 1 && (
          <View style={styles.filterContainer}>
            <SegmentedButtons
              value={channelTypeFilter}
              onValueChange={(value: string) => setChannelTypeFilter(value as ChannelTypeFilter)}
              buttons={filterOptions}
            />
          </View>
        )}

        {/* Channels List */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Channels ({filteredChannels.length})
          </Text>

          {filteredChannels.length === 0 ? (
            <EmptyState
              icon="forum-outline"
              title="No Channels"
              message={
                channelTypeFilter === 'all'
                  ? 'No channels found for this integration'
                  : 'No channels of this type'
              }
            />
          ) : (
            <FlatList
              data={filteredChannels}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => <ChannelCard channel={item} />}
              scrollEnabled={false}
            />
          )}
        </View>
      </Container>
    </ScrollView>
  );
}

interface ChannelCardProps {
  channel: Channel;
}

function ChannelCard({ channel }: ChannelCardProps) {
  return (
    <Card>
      <Card.Content style={styles.channelContent}>
        <View style={styles.channelHeader}>
          <View style={styles.channelInfo}>
            <Text style={styles.channelName}>{channel.channel_name}</Text>
            <View style={styles.channelMeta}>
              <Chip
                mode="outlined"
                compact
                style={styles.typeChip}
                textStyle={styles.typeChipText}
              >
                {getChannelTypeLabel(channel.channel_type)}
              </Chip>
              {channel.member_count !== null && (
                <View style={styles.metaItem}>
                  <Icon source="account-group" size={14} color={colors.textSecondary} />
                  <Text style={styles.metaTextSmall}>{channel.member_count}</Text>
                </View>
              )}
            </View>
          </View>
        </View>

        {channel.description && (
          <Text style={styles.description} numberOfLines={2}>
            {channel.description}
          </Text>
        )}

        <View style={styles.permissions}>
          <PermissionBadge
            icon={channel.can_read_messages ? 'check-circle' : 'close-circle'}
            label="Read Messages"
            granted={channel.can_read_messages}
          />
          <PermissionBadge
            icon={channel.can_read_history ? 'check-circle' : 'close-circle'}
            label="Read History"
            granted={channel.can_read_history}
          />
          {!channel.is_active && (
            <View style={styles.inactiveBadge}>
              <Icon source="alert" size={14} color={colors.warning} />
              <Text style={styles.inactiveText}>Inactive</Text>
            </View>
          )}
        </View>

        {channel.last_synced && (
          <Text style={styles.syncedText}>
            Synced {formatDistanceToNow(new Date(channel.last_synced), { addSuffix: true })}
          </Text>
        )}
      </Card.Content>
    </Card>
  );
}

interface PermissionBadgeProps {
  icon: string;
  label: string;
  granted: boolean;
}

function PermissionBadge({ icon, label, granted }: PermissionBadgeProps) {
  return (
    <View style={styles.permissionBadge}>
      <Icon source={icon} size={14} color={granted ? colors.success : colors.error} />
      <Text style={[styles.permissionText, { color: granted ? colors.success : colors.error }]}>
        {label}
      </Text>
    </View>
  );
}

function getChannelTypeLabel(type: string): string {
  switch (type) {
    case 'discord_server':
      return 'Server';
    case 'discord_channel':
      return 'Channel';
    case 'telegram_group':
      return 'Group';
    case 'telegram_channel':
      return 'Channel';
    default:
      return type;
  }
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
  header: {
    padding: spacing.lg,
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  headerInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  platform: {
    ...typography.headlineSmall,
    color: colors.textPrimary,
  },
  username: {
    ...typography.bodyLarge,
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
  headerMeta: {
    flexDirection: 'row',
    gap: spacing.md,
    flexWrap: 'wrap',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  metaText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
  },
  metaTextSmall: {
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
    marginTop: spacing.md,
  },
  errorText: {
    ...typography.bodySmall,
    color: colors.error,
    flex: 1,
  },
  filterContainer: {
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  section: {
    marginTop: spacing.lg,
  },
  sectionTitle: {
    ...typography.titleLarge,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  channelCard: {
    marginBottom: spacing.md,
  },
  channelContent: {
    padding: spacing.md,
  },
  channelHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  channelInfo: {
    flex: 1,
  },
  channelName: {
    ...typography.titleMedium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  channelMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    flexWrap: 'wrap',
  },
  typeChip: {
    height: 24,
  },
  typeChipText: {
    ...typography.labelMedium,
    fontSize: 11,
  },
  description: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  permissions: {
    flexDirection: 'row',
    gap: spacing.md,
    flexWrap: 'wrap',
    marginBottom: spacing.xs,
  },
  permissionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  permissionText: {
    ...typography.bodySmall,
  },
  inactiveBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  inactiveText: {
    ...typography.bodySmall,
    color: colors.warning,
  },
  syncedText: {
    ...typography.bodySmall,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
});

// Made with Bob