import React from 'react';
import { Button as PaperButton, ButtonProps as PaperButtonProps } from 'react-native-paper';

export interface ButtonProps extends PaperButtonProps {
  children: React.ReactNode;
}

export function Button({ children, ...props }: ButtonProps) {
  return <PaperButton {...props}>{children}</PaperButton>;
}

// Made with Bob
