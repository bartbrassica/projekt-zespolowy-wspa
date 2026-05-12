import React, { createContext, useContext } from 'react';
import type { AuthContextType, AuthProviderProps } from '../types/auth';
import { useAuthState } from '../hooks/useAuthState';
import { useAuthActions } from '../hooks/useAuthActions';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { user, tokens, isLoading, isAuthenticated, setAuthData, clearAuthData } = useAuthState();
  const { login, logout } = useAuthActions({ setAuthData, clearAuthData });

  const value = {
    user,
    tokens,
    login,
    logout,
    isAuthenticated,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Export helper functions from auth API service
// eslint-disable-next-line react-refresh/only-export-components
export { authApi } from '../services/authApi';
