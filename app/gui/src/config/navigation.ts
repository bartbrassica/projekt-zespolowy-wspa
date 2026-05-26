import { Home, Settings } from 'lucide-react';
import type { NavigationItem } from '../types/layout';

export const navigationItems: NavigationItem[] = [
  { name: 'navigation.passwordManager', href: '/passwords', icon: Home },
  { name: 'navigation.settings', href: '/settings', icon: Settings },
];