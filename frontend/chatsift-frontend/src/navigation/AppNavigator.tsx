import React from 'react';
import { NavigationContainer, LinkingOptions, createNavigationContainerRef } from '@react-navigation/native';

export const navigationRef = createNavigationContainerRef<any>();
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
              Integrations: '',
              IntegrationDetail: ':id',
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
    <NavigationContainer ref={navigationRef} linking={linking}>
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
