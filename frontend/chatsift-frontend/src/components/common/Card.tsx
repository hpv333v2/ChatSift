import React from 'react';
import { Card as PaperCard } from 'react-native-paper';
import { ViewStyle, StyleProp } from 'react-native';

export interface CardProps {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  mode?: 'elevated' | 'outlined' | 'contained';
  elevation?: number;
  onPress?: () => void;
  onLongPress?: () => void;
}

export function Card({ children, ...props }: CardProps) {
  return <PaperCard {...(props as any)}>{children}</PaperCard>;
}

Card.Title = PaperCard.Title;
Card.Content = PaperCard.Content;
Card.Actions = PaperCard.Actions;
Card.Cover = PaperCard.Cover;

// Made with Bob
