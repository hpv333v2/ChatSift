import React from 'react';
import { Appbar } from 'react-native-paper';

export interface AppBarProps {
  title: string;
  subtitle?: string;
  back?: boolean;
  onBack?: () => void;
  actions?: React.ReactNode;
}

export function AppBar({ title, subtitle, back, onBack, actions }: AppBarProps) {
  return (
    <Appbar.Header>
      {back && onBack && <Appbar.BackAction onPress={onBack} />}
      <Appbar.Content title={title} subtitle={subtitle} />
      {actions}
    </Appbar.Header>
  );
}

// Made with Bob
