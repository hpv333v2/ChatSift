import React from 'react';
import { View, StyleSheet, ScrollView, ViewStyle } from 'react-native';
import { spacing } from '../../theme/theme';

export interface ContainerProps {
  children: React.ReactNode;
  scrollable?: boolean;
  maxWidth?: number;
  padding?: boolean;
  style?: ViewStyle;
}

export function Container({
  children,
  scrollable = false,
  maxWidth = 1280,
  padding = true,
  style,
}: ContainerProps) {
  const containerStyle = [
    styles.container,
    { maxWidth },
    padding && styles.padding,
    style,
  ];

  if (scrollable) {
    return (
      <ScrollView contentContainerStyle={containerStyle}>
        {children}
      </ScrollView>
    );
  }

  return <View style={containerStyle}>{children}</View>;
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    alignSelf: 'center',
  },
  padding: {
    padding: spacing.md,
  },
});

// Made with Bob
