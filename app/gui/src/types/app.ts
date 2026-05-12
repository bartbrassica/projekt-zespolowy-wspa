import type { ReactNode } from 'react';

export interface ProtectedRouteProps {
  children: ReactNode;
}

export interface RouteConfig {
  path: string;
  element: ReactNode;
  isProtected?: boolean;
  redirectIfAuthenticated?: boolean;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export interface AppRoutes {
  public: RouteConfig[];
  protected: RouteConfig[];
  auth: RouteConfig[];
}