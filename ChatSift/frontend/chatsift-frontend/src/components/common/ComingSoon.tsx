import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Icon, Button } from 'react-native-paper';
import { spacing, colors } from '../../theme/theme';

export interface ComingSoonProps {
  icon?: string;
  title: string;
  description: string;
}

export function ComingSoon({ icon = 'rocket-launch', title, description }: ComingSoonProps) {
  return (
    <View style={styles.container}>
      <Icon source={icon} size={80} color={colors.primary} />
      <Text variant="headlineMedium" style={styles.title}>
        {title}
      </Text>
      <Text variant="bodyLarge" style={styles.description}>
        {description}
      </Text>
      <Button mode="contained" disabled style={styles.button}>
        Coming Soon
      </Button>
      <Button mode="text" onPress={() => {}} style={styles.notifyButton}>
        Notify Me
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  title: {
    marginTop: spacing.lg,
    textAlign: 'center',
    color: colors.textPrimary,
  },
  description: {
    marginTop: spacing.md,
    textAlign: 'center',
    color: colors.textSecondary,
    maxWidth: 400,
  },
  button: {
    marginTop: spacing.xl,
  },
  notifyButton: {
    marginTop: spacing.sm,
  },
});

// Made with Bob
