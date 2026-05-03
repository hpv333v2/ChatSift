import React from 'react';
import { TextInput, TextInputProps } from 'react-native-paper';

export interface InputProps extends Omit<TextInputProps, 'theme'> {}

export function Input(props: InputProps) {
  return <TextInput {...props} />;
}

// Made with Bob
