import React from 'react';
import { StyleSheet } from 'react-native';
import { Banner, BannerProps } from 'react-native-paper';
import { spacing } from '../../theme/theme';

export interface ErrorBannerProps extends Omit<BannerProps, 'children' | 'visible' | 'onDismiss'> {
  message: string;
  visible?: boolean;
  onDismiss?: () => void;
  onRetry?: () => void;
  action?: {
    label: string;
    onPress: () => void;
  };
}

export function ErrorBanner({ message, action, visible = true, onDismiss, onRetry, ...props }: ErrorBannerProps) {
  const actions = [];
  
  if (onRetry) {
    actions.push({ label: 'Retry', onPress: onRetry });
  }
  
  if (action) {
    actions.push({ label: action.label, onPress: action.onPress });
  }
  
  if (onDismiss) {
    actions.push({ label: 'Dismiss', onPress: onDismiss });
  }
  return (
    <Banner
      visible={visible}
      actions={actions}
      icon="alert-circle"
      style={styles.banner}
      {...props}
    >
      {message}
    </Banner>
  );
}

const styles = StyleSheet.create({
  banner: {
    marginBottom: spacing.sm,
  },
});

// Made with Bob
