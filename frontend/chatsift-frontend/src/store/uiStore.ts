import { create } from 'zustand';

interface SnackbarItem {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

interface UiState {
  snackbarQueue: SnackbarItem[];
  showSnackbar: (message: string, type?: 'success' | 'error' | 'info' | 'warning') => void;
  dismissSnackbar: (id: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  snackbarQueue: [],
  showSnackbar: (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') =>
    set((state) => ({
      snackbarQueue: [
        ...state.snackbarQueue,
        {
          id: Date.now().toString(),
          message,
          type,
        },
      ],
    })),
  dismissSnackbar: (id: string) =>
    set((state) => ({
      snackbarQueue: state.snackbarQueue.filter((item) => item.id !== id),
    })),
}));

// Made with Bob
