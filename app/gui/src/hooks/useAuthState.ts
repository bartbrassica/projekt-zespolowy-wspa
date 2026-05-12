import { useState, useEffect } from 'react';
import type { User, AuthTokens } from '../types/auth';
import { authStorage } from '../utils/authStorage';

export const useAuthState = () => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const authData = authStorage.getAuthData();

    if (authData) {
      setTokens(authData.tokens);
      setUser(authData.user);
    }

    setIsLoading(false);
  }, []);

  const setAuthData = (newTokens: AuthTokens, newUser: User) => {
    setTokens(newTokens);
    setUser(newUser);
  };

  const clearAuthData = () => {
    setUser(null);
    setTokens(null);
    authStorage.clearAuthData();
  };

  return {
    user,
    tokens,
    isLoading,
    isAuthenticated: !!user && !!tokens,
    setAuthData,
    clearAuthData
  };
};