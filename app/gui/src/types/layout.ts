import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

export interface LayoutProps {
  children: ReactNode;
}

export interface NavigationItem {
  name: string;
  href: string;
  icon: LucideIcon;
}

export interface HeaderProps {
  user: { email: string } | null;
  onLogout: () => void;
}

export interface NavigationProps {
  items: NavigationItem[];
  currentPath: string;
}

export interface UserMenuProps {
  user: { email: string } | null;
  onLogout: () => void;
}

export interface BrandLogoProps {
  className?: string;
}