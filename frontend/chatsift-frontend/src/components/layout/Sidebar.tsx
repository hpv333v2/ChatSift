import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Drawer, Divider } from 'react-native-paper';
import { spacing, colors } from '../../theme/theme';

export interface SidebarItem {
  key: string;
  label: string;
  icon: string;
  active?: boolean;
  onPress: () => void;
}

export interface SidebarProps {
  items: SidebarItem[];
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

export function Sidebar({ items, header, footer }: SidebarProps) {
  return (
    <View style={styles.container}>
      {header && (
        <>
          <View style={styles.header}>{header}</View>
          <Divider />
        </>
      )}
      <ScrollView style={styles.content}>
        {items.map((item) => (
          <Drawer.Item
            key={item.key}
            label={item.label}
            icon={item.icon}
            active={item.active}
            onPress={item.onPress}
          />
        ))}
      </ScrollView>
      {footer && (
        <>
          <Divider />
          <View style={styles.footer}>{footer}</View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: 280,
    backgroundColor: colors.surface,
    borderRightWidth: 1,
    borderRightColor: colors.border,
  },
  header: {
    padding: spacing.md,
  },
  content: {
    flex: 1,
  },
  footer: {
    padding: spacing.md,
  },
});

// Made with Bob
