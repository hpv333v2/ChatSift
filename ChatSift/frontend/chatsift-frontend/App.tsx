import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { PaperProvider, Snackbar } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppNavigator } from './src/navigation/AppNavigator';
import { useAuthStore } from './src/store/authStore';
import { useUiStore } from './src/store/uiStore';
import { theme } from './src/theme/theme';
import { Loading } from './src/components/common/Loading';
import { colors } from './src/theme/theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

function GlobalSnackbar() {
  const { snackbarQueue, dismissSnackbar } = useUiStore();
  const currentSnackbar = snackbarQueue[0];

  if (!currentSnackbar) return null;

  const getBackgroundColor = () => {
    switch (currentSnackbar.type) {
      case 'success':
        return colors.success;
      case 'error':
        return colors.error;
      case 'warning':
        return colors.warning;
      case 'info':
      default:
        return colors.info;
    }
  };

  return (
    <Snackbar
      visible={!!currentSnackbar}
      onDismiss={() => dismissSnackbar(currentSnackbar.id)}
      duration={4000}
      style={{ backgroundColor: getBackgroundColor() }}
      action={{
        label: 'Dismiss',
        onPress: () => dismissSnackbar(currentSnackbar.id),
      }}
    >
      {currentSnackbar.message}
    </Snackbar>
  );
}

export default function App() {
  const { checkAuth, isLoading } = useAuthStore();
  const [isInitialized, setIsInitialized] = React.useState(false);

  React.useEffect(() => {
    const initialize = async () => {
      await checkAuth();
      setIsInitialized(true);
    };

    initialize();
  }, [checkAuth]);

  if (!isInitialized || isLoading) {
    return (
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <Loading message="Initializing..." />
        </PaperProvider>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <PaperProvider theme={theme}>
          <AppNavigator />
          <GlobalSnackbar />
        </PaperProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}

// Made with Bob
