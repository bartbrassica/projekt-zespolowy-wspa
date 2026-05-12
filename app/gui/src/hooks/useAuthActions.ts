import { useCallback } from 'react';
import type { User, AuthTokens } from '../types/auth';
import { authApi } from '../services/authApi';
import { authStorage } from '../utils/authStorage';

interface UseAuthActionsProps {
  setAuthData: (tokens: AuthTokens, user: User) => void;
  clearAuthData: () => void;
}

export const useAuthActions = ({ setAuthData, clearAuthData }: UseAuthActionsProps) => {
  const login = useCallback(async (email: string, password: string, remember_me: boolean) => {
    try {
      const tokens = await authApi.login({ email, password, remember_me });
      const user = { email };

      setAuthData(tokens, user);
      authStorage.setAuthData(tokens, user, remember_me);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, [setAuthData]);

  const logout = useCallback(() => {
    clearAuthData();
  }, [clearAuthData]);

  return {
    login,
    logout
  };
};