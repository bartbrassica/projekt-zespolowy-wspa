import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../store/auth';
import type { LoginFormData } from '../types/auth';

export const useLogin = (onSuccess?: () => void) => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (formData: LoginFormData) => {
    setError('');
    setIsLoading(true);

    try {
      await login(formData.email, formData.password, formData.rememberMe);
      onSuccess?.();
      navigate('/passwords');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    handleLogin,
    isLoading,
    error
  };
};