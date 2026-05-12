import { useState } from 'react';
import type { ForgotPasswordRequest } from '../types/password-reset';

export const useForgotPassword = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const requestPasswordReset = async (email: string) => {
    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await fetch('/api/password/reset/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email } as ForgotPasswordRequest),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
      } else {
        setError(data.message || 'Failed to send reset email');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError('');
  const clearSuccess = () => setSuccess(false);

  return {
    isLoading,
    error,
    success,
    requestPasswordReset,
    clearError,
    clearSuccess,
  };
};
