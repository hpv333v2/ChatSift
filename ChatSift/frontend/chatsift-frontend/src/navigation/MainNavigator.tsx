import React from 'react';
import { View, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Icon } from 'react-native-paper';
import { useResponsive } from '../hooks/useResponsive';
import { Sidebar, SidebarItem } from '../components/layout/Sidebar';
import { colors } from '../theme/theme';
import { DashboardScreen } from '../screens/DashboardScreen';
import { IntegrationsScreen } from '../screens/IntegrationsScreen';
import { IntegrationDetailScreen } from '../screens/IntegrationDetailScreen';
import { MonitoringScreen } from '../screens/MonitoringScreen';
import { SummariesScreen } from '../screens/SummariesScreen';
import { SettingsScreen } from '../screens/SettingsScreen';

export type MainTabParamList = {
  Dashboard: undefined;
  Integrations: undefined;
  IntegrationDetail: { id: string };
  Monitoring: undefined;
  Summaries: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator<MainTabParamList>();

// Integrations Stack Navigator (for detail screen)
function IntegrationsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Integrations" component={IntegrationsScreen} />
      <Stack.Screen name="IntegrationDetail" component={IntegrationDetailScreen} />
    </Stack.Navigator>
  );
}

export function MainNavigator() {
  const { isMobile } = useResponsive();

  if (isMobile) {
    // Mobile: bottom tabs
    return (
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.textSecondary,
        }}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{
            tabBarIcon: ({ color, size }: { color: string; size: number }) => (
              <Icon source="view-dashboard" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Integrations"
          component={IntegrationsStack}
          options={{
            tabBarIcon: ({ color, size }: { color: string; size: number }) => (
              <Icon source="connection" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Monitoring"
          component={MonitoringScreen}
          options={{
            tabBarIcon: ({ color, size }: { color: string; size: number }) => (
              <Icon source="monitor" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Summaries"
          component={SummariesScreen}
          options={{
            tabBarIcon: ({ color, size }: { color: string; size: number }) => (
              <Icon source="file-document" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            tabBarIcon: ({ color, size }: { color: string; size: number }) => (
              <Icon source="cog" size={size} color={color} />
            ),
          }}
        />
      </Tab.Navigator>
    );
  }

  // Tablet+: sidebar layout with stack navigator
  return (
    <View style={styles.desktopContainer}>
      <SidebarNavigator />
      <View style={styles.content}>
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: { display: 'none' },
          }}
        >
          <Tab.Screen name="Dashboard" component={DashboardScreen} />
          <Tab.Screen name="Integrations" component={IntegrationsStack} />
          <Tab.Screen name="Monitoring" component={MonitoringScreen} />
          <Tab.Screen name="Summaries" component={SummariesScreen} />
          <Tab.Screen name="Settings" component={SettingsScreen} />
        </Tab.Navigator>
      </View>
    </View>
  );
}

function SidebarNavigator() {
  const [activeRoute, setActiveRoute] = React.useState('Dashboard');

  const items: SidebarItem[] = [
    {
      key: 'Dashboard',
      label: 'Dashboard',
      icon: 'view-dashboard',
      active: activeRoute === 'Dashboard',
      onPress: () => setActiveRoute('Dashboard'),
    },
    {
      key: 'Integrations',
      label: 'Integrations',
      icon: 'connection',
      active: activeRoute === 'Integrations',
      onPress: () => setActiveRoute('Integrations'),
    },
    {
      key: 'Monitoring',
      label: 'Monitoring',
      icon: 'monitor',
      active: activeRoute === 'Monitoring',
      onPress: () => setActiveRoute('Monitoring'),
    },
    {
      key: 'Summaries',
      label: 'Summaries',
      icon: 'file-document',
      active: activeRoute === 'Summaries',
      onPress: () => setActiveRoute('Summaries'),
    },
    {
      key: 'Settings',
      label: 'Settings',
      icon: 'cog',
      active: activeRoute === 'Settings',
      onPress: () => setActiveRoute('Settings'),
    },
  ];

  return <Sidebar items={items} />;
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  desktopContainer: {
    flex: 1,
    flexDirection: 'row',
  },
  content: {
    flex: 1,
  },
});

// Made with Bob
