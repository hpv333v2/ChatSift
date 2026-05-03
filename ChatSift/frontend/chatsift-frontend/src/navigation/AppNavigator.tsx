import React from 'react';
import { NavigationContainer, LinkingOptions } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { AuthNavigator } from './AuthNavigator';
import { MainNavigator } from './MainNavigator';
import { useAuthStore } from '../store/authStore';
import { Loading } from '../components/common/Loading';

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const linking: LinkingOptions<RootStackParamList> = {
  prefixes: ['chatsift://', 'https://chatsift.app'],
  config: {
    screens: {
      Auth: {
        screens: {
          Login: 'login',
          Register: 'register',
          EmailVerification: 'verify-email',
        },
      },
      Main: {
        screens: {
          Dashboard: 'dashboard',
          Integrations: {
            path: 'integrations',
            screens: {
              IntegrationsList: '',
              IntegrationDetail: ':id',
              DiscordCallback: 'discord/callback',
            },
          },
          Monitoring: 'monitoring',
          Summaries: 'summaries',
          Settings: 'settings',
        },
      },
    },
  },
};

export function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return <Loading message="Loading..." />;
  }

  return (
    <NavigationContainer linking={linking}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Made with Bob
