# 🎨 ChatSift Frontend - Master Implementation Plan
## React Native Universal App (Web + iOS + Android)

---

## 🎯 Executive Summary

**Mission**: Build a stunning, professional React Native frontend that works seamlessly across web and mobile platforms, impressing professionals with exceptional UI/UX design and thoughtful architecture.

**Constraints**: 
- 30 tokens total budget (planning + implementation + testing)
- Must deliver working PoC
- Backend already built (Django REST API)
- Single codebase for all platforms

---

## 📚 Tech Stack (Optimized for Speed & Quality)

```json
{
  "core": {
    "react-native": "0.73.x",
    "react-native-web": "0.19.x", 
    "expo": "~50.0.x"
  },
  "ui": {
    "react-native-paper": "^5.12.0",
    "react-native-vector-icons": "^10.0.0",
    "react-native-reanimated": "^3.6.0"
  },
  "state": {
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0"
  },
  "navigation": {
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/native-stack": "^6.9.0",
    "@react-navigation/bottom-tabs": "^6.5.0"
  },
  "forms": {
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0"
  },
  "utils": {
    "@react-native-async-storage/async-storage": "^1.21.0",
    "date-fns": "^3.0.0",
    "jwt-decode": "^4.0.0"
  }
}
```

---

## 🎨 Design System (Material Design 3)

### Color Palette
```javascript
const colors = {
  primary: '#6750A4',      // Deep Purple
  secondary: '#625B71',    // Muted Purple  
  tertiary: '#7D5260',     // Warm Rose
  success: '#2E7D32',
  error: '#B3261E',
  warning: '#F57C00',
  surface: '#FFFBFE',
  text: {
    primary: '#1C1B1F',
    secondary: '#49454F'
  }
};
```

### Typography (8px base grid)
```javascript
const typography = {
  displayLarge: { fontSize: 57, fontWeight: '400' },
  headlineMedium: { fontSize: 28, fontWeight: '400' },
  titleLarge: { fontSize: 22, fontWeight: '500' },
  bodyLarge: { fontSize: 16, fontWeight: '400' },
  labelLarge: { fontSize: 14, fontWeight: '500' }
};
```

### Spacing
```javascript
const spacing = {
  xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48
};
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/                    # API integration
│   │   ├── client.ts          # Axios with interceptors
│   │   ├── auth.ts            # Auth endpoints
│   │   ├── integrations.ts    # Platform connections
│   │   ├── monitoring.ts      # Channel monitoring
│   │   └── summaries.ts       # Summary endpoints
│   │
│   ├── components/            # Reusable components
│   │   ├── common/           # Button, Card, Input, Modal
│   │   ├── layout/           # AppBar, Sidebar, Container
│   │   └── features/         # Feature-specific
│   │
│   ├── screens/              # Screen components
│   │   ├── auth/            # Login, Register, Verify
│   │   ├── dashboard/       # Main dashboard
│   │   ├── integrations/    # Platform connections
│   │   ├── monitoring/      # Channel monitoring
│   │   ├── summaries/       # Summary views
│   │   └── settings/        # User settings
│   │
│   ├── navigation/          # Navigation setup
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── MainNavigator.tsx
│   │
│   ├── store/              # State management
│   │   ├── auth.store.ts   # Auth state (Zustand)
│   │   ├── theme.store.ts  # Theme state
│   │   └── ui.store.ts     # UI state
│   │
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useIntegrations.ts
│   │   ├── useMonitoring.ts
│   │   └── useSummaries.ts
│   │
│   ├── theme/              # Theme config
│   │   └── theme.ts
│   │
│   └── utils/              # Utilities
│       ├── storage.ts
│       └── validation.ts
│
├── app.json               # Expo config
├── package.json
└── tsconfig.json
```

---

## 🔐 Authentication Flow

```
App Launch → Check Token → Valid? → Main App
                ↓ Invalid
            Login Screen → Register/Login → Email Verify → Onboarding → Main App
```

**Key Features**:
- JWT token management with auto-refresh
- Secure token storage (AsyncStorage/SecureStore)
- Email verification flow
- Protected routes

---

## 📱 Core Screens & Layouts

### 1. Login Screen
```
┌─────────────────────────┐
│  [Logo]                 │
│  Welcome Back           │
│                         │
│  ┌───────────────────┐  │
│  │ Email           │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ Password    [👁] │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │   Sign In        │  │
│  └───────────────────┘  │
│                         │
│  Don't have account?    │
└─────────────────────────┘
```

### 2. Dashboard (Mobile)
```
┌─────────────────────────┐
│ [☰] ChatSift    [🔔][👤]│
├─────────────────────────┤
│ ┌─────────┐ ┌─────────┐│
│ │ Active  │ │ Today's ││
│ │ Channels│ │ Activity││
│ │   12    │ │ 245 msg ││
│ └─────────┘ └─────────┘│
│                         │
│ Recent Summaries        │
│ ┌─────────────────────┐│
│ │ 📱 #general         ││
│ │ 45 msgs • 2h ago    ││
│ │ [View]              ││
│ └─────────────────────┘│
│ ┌─────────────────────┐│
│ │ 💬 Dev Team         ││
│ │ 89 msgs • 5h ago    ││
│ │ [View]              ││
│ └─────────────────────┘│
├─────────────────────────┤
│ [📊][🔗][📺][📝][⚙️]   │
└─────────────────────────┘
```

### 3. Dashboard (Desktop)
```
┌────────────────────────────────────────┐
│ [☰] ChatSift  [🔍]    [🔔][👤][⚙️]   │
├────┬───────────────────────────────────┤
│📊  │ Dashboard                         │
│🔗  │ ┌────────┐ ┌────────┐ ┌────────┐│
│📺  │ │Active  │ │Today's │ │Success ││
│📝  │ │  12    │ │245 msg │ │  98%   ││
│⚙️  │ └────────┘ └────────┘ └────────┘│
│    │                                   │
│    │ Recent Summaries                  │
│    │ [Summary cards with details...]   │
│    │                                   │
│    │ Activity Chart                    │
│    │ [Line chart visualization...]     │
└────┴───────────────────────────────────┘
```

### 4. Integrations Screen
```
┌─────────────────────────┐
│ Platform Connections    │
│                         │
│ Connected (2)           │
│ ┌─────────────────────┐│
│ │ [Discord]           ││
│ │ @username           ││
│ │ 8 servers           ││
│ │ [Refresh][Disconnect]│
│ └─────────────────────┘│
│ ┌─────────────────────┐│
│ │ [Telegram]          ││
│ │ @username           ││
│ │ 5 groups            ││
│ │ [Refresh][Disconnect]│
│ └─────────────────────┘│
│                         │
│ ┌─────────────────────┐│
│ │ [+] Add Platform    ││
│ └─────────────────────┘│
└─────────────────────────┘
```

### 5. Monitoring Screen
```
┌─────────────────────────┐
│ Channel Monitoring      │
│ [+ Add]      [Filter ▼]│
│                         │
│ Active (5)              │
│ ┌─────────────────────┐│
│ │ 📱 #general         ││
│ │ ● Active • Hourly   ││
│ │ Last: 15m • 234 msg ││
│ │ [⚙️][⏸]            ││
│ └─────────────────────┘│
│ ┌─────────────────────┐│
│ │ 💬 Dev Team         ││
│ │ ● Active • 6h       ││
│ │ Last: 2h • 89 msg   ││
│ │ [⚙️][⏸]            ││
│ └─────────────────────┘│
└─────────────────────────┘
```

### 6. Summaries Screen
```
┌─────────────────────────┐
│ Summaries               │
│ [📅 Today ▼] [🔍]      │
│                         │
│ Today - May 3           │
│ ┌─────────────────────┐│
│ │ 📱 #general         ││
│ │ 9:00 AM • 45 msgs   ││
│ │                     ││
│ │ 🔑 Key Points       ││
│ │ • Deadline extended ││
│ │ • Feature approved  ││
│ │                     ││
│ │ ✅ Decisions        ││
│ │ • Use React Native  ││
│ │                     ││
│ │ [View Full]         ││
│ └─────────────────────┘│
└─────────────────────────┘
```

---

## 🔄 State Management

### Zustand (Client State)
```typescript
// Auth Store
interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  login: (tokens, user) => void;
  logout: () => void;
}

// Theme Store
interface ThemeState {
  mode: 'light' | 'dark';
  setMode: (mode) => void;
}

// UI Store
interface UIState {
  toast: ToastState | null;
  showToast: (toast) => void;
}
```

### React Query (Server State)
```typescript
// Fetch integrations
const useIntegrations = () => {
  return useQuery({
    queryKey: ['integrations'],
    queryFn: api.integrations.list,
    staleTime: 5 * 60 * 1000
  });
};

// Fetch summaries with pagination
const useSummaries = () => {
  return useInfiniteQuery({
    queryKey: ['summaries'],
    queryFn: ({ pageParam = 1 }) => 
      api.summaries.list({ page: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextPage
  });
};

// Connect Discord mutation
const useConnectDiscord = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.integrations.connectDiscord,
    onSuccess: () => {
      queryClient.invalidateQueries(['integrations']);
    }
  });
};
```

---

## 🌐 API Integration

### Axios Client with Auto-Refresh
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000
});

// Add auth token
apiClient.interceptors.request.use(async (config) => {
  const tokens = await getTokens();
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const tokens = await getTokens();
      const { data } = await axios.post('/auth/refresh/', {
        refresh: tokens.refresh
      });
      await saveTokens(data.tokens);
      error.config.headers.Authorization = `Bearer ${data.tokens.access}`;
      return apiClient(error.config);
    }
    return Promise.reject(error);
  }
);
```

### API Endpoints
```typescript
export const api = {
  auth: {
    register: (data) => apiClient.post('/auth/register/', data),
    login: (data) => apiClient.post('/auth/login/', data),
    logout: (refresh) => apiClient.post('/auth/logout/', { refresh }),
    refresh: (refresh) => apiClient.post('/auth/refresh/', { refresh }),
    verifyEmail: (token, uid) => 
      apiClient.post('/auth/email/verify/confirm/', { token, uid }),
    getCurrentUser: () => apiClient.get('/users/me/')
  },
  
  integrations: {
    list: () => apiClient.get('/integrations/'),
    getDiscordAuthUrl: () => apiClient.get('/integrations/discord/authorize/'),
    connectTelegram: (botToken) => 
      apiClient.post('/integrations/telegram/connect/', { bot_token: botToken }),
    disconnect: (id) => apiClient.delete(`/integrations/${id}/`),
    refresh: (id) => apiClient.post(`/integrations/${id}/refresh/`)
  },
  
  monitoring: {
    list: (params) => apiClient.get('/monitoring/channels/', { params }),
    add: (data) => apiClient.post('/monitoring/channels/', data),
    update: (id, data) => apiClient.patch(`/monitoring/channels/${id}/`, data),
    toggle: (id) => apiClient.post(`/monitoring/channels/${id}/toggle/`),
    remove: (id) => apiClient.delete(`/monitoring/channels/${id}/`),
    getAvailable: () => apiClient.get('/monitoring/channels/available/'),
    getStats: () => apiClient.get('/monitoring/channels/stats/')
  },
  
  summaries: {
    list: (params) => apiClient.get('/summaries/', { params }),
    get: (id) => apiClient.get(`/summaries/${id}/`),
    regenerate: (id) => apiClient.post(`/summaries/${id}/regenerate/`),
    delete: (id) => apiClient.delete(`/summaries/${id}/`),
    getLatest: () => apiClient.get('/summaries/latest/')
  }
};
```

---

## 🎭 Key Components

### Button Component
```typescript
interface ButtonProps {
  variant: 'filled' | 'outlined' | 'text';
  size: 'small' | 'medium' | 'large';
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  children: ReactNode;
}
```

### Card Component
```typescript
interface CardProps {
  elevation?: 0 | 1 | 2 | 3;
  onPress?: () => void;
  children: ReactNode;
}
```

### Input Component
```typescript
interface InputProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  secureTextEntry?: boolean;
}
```

---

## 📱 Responsive Design

### Breakpoints
```typescript
const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024
};

const useResponsive = () => {
  const { width } = useWindowDimensions();
  return {
    isMobile: width < 768,
    isTablet: width >= 768 && width < 1024,
    isDesktop: width >= 1024
  };
};
```

### Adaptive Layout
```typescript
const DashboardScreen = () => {
  const { isMobile, isDesktop } = useResponsive();
  
  return (
    <View style={styles.container}>
      {isDesktop && <Sidebar />}
      <View style={styles.content}>
        <Header />
        <StatsCards columns={isMobile ? 2 : 4} />
        <RecentSummaries />
      </View>
    </View>
  );
};
```

---

## ♿ Accessibility

- Screen reader support (accessibilityLabel)
- Keyboard navigation (web)
- Color contrast WCAG AA (4.5:1)
- Touch targets 44x44 minimum
- Dynamic text scaling
- Reduced motion support

---

## 🚀 Performance Optimization

1. **Code Splitting**: Lazy load screens
2. **List Virtualization**: FlatList for long lists
3. **Memoization**: React.memo, useMemo, useCallback
4. **Image Optimization**: Optimized formats, lazy loading
5. **Caching**: React Query + AsyncStorage
6. **Bundle Size**: Tree shaking, remove unused deps

---

## 📋 Implementation Roadmap (Priority Order)

### Phase 1: Foundation (Token Budget: 8)
```
[x] Project setup with Expo
[x] Design system implementation
[x] Navigation structure
[x] API client with interceptors
[x] Auth store (Zustand)
[x] Theme configuration
[ ] Common components (Button, Card, Input)
[ ] Layout components (AppBar, Container)
```

### Phase 2: Authentication (Token Budget: 6)
```
[ ] Login screen
[ ] Register screen
[ ] Email verification screen
[ ] Auth flow integration
[ ] Token management
[ ] Protected routes
```

### Phase 3: Core Features (Token Budget: 10)
```
[ ] Dashboard screen
[ ] Integrations screen
[ ] Discord OAuth flow
[ ] Telegram connect flow
[ ] Monitoring screen
[ ] Channel selection
[ ] Summaries screen
[ ] Summary detail screen
```

### Phase 4: Polish & Testing (Token Budget: 6)
```
[ ] Responsive layouts
[ ] Loading states
[ ] Error handling
[ ] Empty states
[ ] Animations
[ ] Accessibility
[ ] Testing
[ ] Bug fixes
```

---

## 🎯 Success Criteria

### Functional Requirements
✅ User can register and login  
✅ User can connect Discord/Telegram  
✅ User can select channels to monitor  
✅ User can view summaries  
✅ Works on web, iOS, Android  

### Design Requirements
✅ Modern Material Design 3 UI  
✅ Smooth animations and transitions  
✅ Responsive across all screen sizes  
✅ Professional color scheme  
✅ Consistent spacing and typography  

### Technical Requirements
✅ Single codebase for all platforms  
✅ Type-safe with TypeScript  
✅ Optimized performance  
✅ Secure token management  
✅ Error handling and loading states  

---

## 💡 Key Design Principles

1. **Simplicity**: Clean, uncluttered interfaces
2. **Consistency**: Uniform design language throughout
3. **Feedback**: Clear visual feedback for all actions
4. **Efficiency**: Minimize steps to complete tasks
5. **Accessibility**: Usable by everyone
6. **Performance**: Fast, smooth, responsive

---

## 🔧 Development Commands

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on web
npm run web

# Run on iOS
npm run ios

# Run on Android
npm run android

# Build for production
npm run build
```

---

## 📦 Package.json (Essential Dependencies)

```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.73.2",
    "react-native-web": "0.19.9",
    "expo": "~50.0.0",
    "react-native-paper": "^5.12.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/native-stack": "^6.9.17",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.5",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "date-fns": "^3.2.0",
    "jwt-decode": "^4.0.0",
    "react-native-vector-icons": "^10.0.3",
    "react-native-reanimated": "^3.6.1"
  },
  "devDependencies": {
    "@types/react": "~18.2.45",
    "@types/react-native": "~0.73.0",
    "typescript": "^5.3.3"
  }
}
```

---

## 🎨 Design Inspiration & References

- **Material Design 3**: https://m3.material.io/
- **iOS Human Interface Guidelines**: https://developer.apple.com/design/
- **React Native Paper**: https://callstack.github.io/react-native-paper/
- **Expo Documentation**: https://docs.expo.dev/

---

## 📝 Notes for AI Implementation

### Critical Success Factors
1. **Use Expo** for rapid development and easy deployment
2. **React Native Paper** for pre-built Material Design components
3. **React Query** for efficient server state management
4. **Zustand** for lightweight client state
5. **TypeScript** for type safety and better DX

### Time-Saving Tips
1. Use Paper's built-in components (Button, Card, TextInput)
2. Leverage React Query's caching and auto-refetch
3. Use Expo's managed workflow (no native code needed)
4. Copy-paste design system values from this plan
5. Focus on core user flows first, polish later

### Common Pitfalls to Avoid
1. Don't over-engineer state management
2. Don't create custom components when Paper has them
3. Don't forget responsive design from the start
4. Don't skip error handling and loading states
5. Don't ignore accessibility attributes

---

## 🏆 Expected Outcome

A **professional, modern, responsive** React Native application that:
- Impresses with clean Material Design 3 UI
- Works flawlessly on web, iOS, and Android
- Provides smooth, intuitive user experience
- Demonstrates thoughtful architecture and design
- Serves as a solid foundation for future features

**This frontend will turn heads and showcase the power of React Native for universal app development!** 🚀

---

*Made with ❤️ by Bob - Your AI Planning Assistant*