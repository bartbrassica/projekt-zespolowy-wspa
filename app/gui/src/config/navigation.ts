import { Home, Settings } from 'lucide-react';
import type { NavigationItem } from '../types/layout';

export const navigationItems: NavigationItem[] = [
  { name: 'Password Manager', href: '/passwords', icon: Home },
  { name: 'Settings', href: '/settings', icon: Settings },
];