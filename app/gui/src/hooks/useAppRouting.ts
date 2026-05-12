import { useAuth } from '../store/auth';

export const useAppRouting = () => {
  const { isAuthenticated } = useAuth();

  const shouldRedirectToPasswords = (path: string): boolean => {
    return isAuthenticated && (path === '/login' || path === '/register');
  };

  const getRedirectPath = (): string => {
    return isAuthenticated ? '/passwords' : '/login';
  };

  return {
    isAuthenticated,
    shouldRedirectToPasswords,
    getRedirectPath
  };
};