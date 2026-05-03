import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { useResponsive } from '../../hooks/useResponsive';
import { spacing } from '../../theme/theme';

export interface ResponsiveGridProps {
  children: React.ReactNode;
  columns?: {
    mobile?: number;
    tablet?: number;
    desktop?: number;
    wide?: number;
  };
  gap?: number;
  style?: ViewStyle;
}

export function ResponsiveGrid({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 3, wide: 4 },
  gap = spacing.md,
  style,
}: ResponsiveGridProps) {
  const { breakpoint } = useResponsive();

  const columnCount = columns[breakpoint] || columns.mobile || 1;

  const childArray = React.Children.toArray(children);

  return (
    <View style={[styles.container, style]}>
      {childArray.map((child, index) => (
        <View
          key={index}
          style={[
            styles.item,
            {
              width: `${100 / columnCount}%`,
              padding: gap / 2,
            },
          ]}
        >
          {child}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing.md / 2,
  },
  item: {
    marginBottom: spacing.md,
  },
});

// Made with Bob
