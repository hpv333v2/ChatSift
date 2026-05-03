import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const colors = {
  primary: '#6750A4',
  primaryLight: '#9A82DB',
  primaryDark: '#4F378B',
  secondary: '#625B71',
  tertiary: '#7D5260',
  success: '#2E7D32',
  error: '#B3261E',
  warning: '#F57C00',
  info: '#0288D1',
  surface: '#FFFBFE',
  surfaceVariant: '#E7E0EC',
  background: '#FFFBFE',
  textPrimary: '#1C1B1F',
  textSecondary: '#49454F',
  textTertiary: '#79747E',
  border: '#CAC4D0',
  divider: '#E7E0EC',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const radius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 28,
  full: 9999,
};

export const typography = {
  displayLarge: { fontSize: 57, fontWeight: '400' as const, lineHeight: 64 },
  displayMedium: { fontSize: 45, fontWeight: '400' as const, lineHeight: 52 },
  headlineLarge: { fontSize: 32, fontWeight: '400' as const, lineHeight: 40 },
  headlineMedium: { fontSize: 28, fontWeight: '400' as const, lineHeight: 36 },
  headlineSmall: { fontSize: 24, fontWeight: '400' as const, lineHeight: 32 },
  titleLarge: { fontSize: 22, fontWeight: '500' as const, lineHeight: 28 },
  titleMedium: { fontSize: 16, fontWeight: '500' as const, lineHeight: 24 },
  titleSmall: { fontSize: 14, fontWeight: '500' as const, lineHeight: 20 },
  bodyLarge: { fontSize: 16, fontWeight: '400' as const, lineHeight: 24 },
  bodyMedium: { fontSize: 14, fontWeight: '400' as const, lineHeight: 20 },
  bodySmall: { fontSize: 12, fontWeight: '400' as const, lineHeight: 16 },
  labelLarge: { fontSize: 14, fontWeight: '500' as const, lineHeight: 20 },
  labelMedium: { fontSize: 12, fontWeight: '500' as const, lineHeight: 16 },
} as const;

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    secondary: colors.secondary,
    tertiary: colors.tertiary,
    error: colors.error,
    surface: colors.surface,
    surfaceVariant: colors.surfaceVariant,
    background: colors.background,
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onTertiary: '#FFFFFF',
    onSurface: colors.textPrimary,
    onSurfaceVariant: colors.textSecondary,
    onBackground: colors.textPrimary,
    outline: colors.border,
    outlineVariant: colors.divider,
  },
};

// Made with Bob
