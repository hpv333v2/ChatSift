import { useWindowDimensions } from 'react-native';

export type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'wide';

export interface ResponsiveValues {
  breakpoint: Breakpoint;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isWide: boolean;
  width: number;
  height: number;
}

const BREAKPOINTS = {
  mobile: 0,
  tablet: 600,
  desktop: 960,
  wide: 1440,
} as const;

export function useResponsive(): ResponsiveValues {
  const { width, height } = useWindowDimensions();

  const getBreakpoint = (): Breakpoint => {
    if (width >= BREAKPOINTS.wide) return 'wide';
    if (width >= BREAKPOINTS.desktop) return 'desktop';
    if (width >= BREAKPOINTS.tablet) return 'tablet';
    return 'mobile';
  };

  const breakpoint = getBreakpoint();

  return {
    breakpoint,
    isMobile: breakpoint === 'mobile',
    isTablet: breakpoint === 'tablet',
    isDesktop: breakpoint === 'desktop',
    isWide: breakpoint === 'wide',
    width,
    height,
  };
}

// Made with Bob
