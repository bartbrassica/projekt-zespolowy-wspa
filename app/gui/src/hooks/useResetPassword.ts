import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import i18next from 'i18next';
import type { ResetPasswordRequest } from '../types/password-reset';
import { validateNewPassword, passwordsMatch } from '../utils/passwordResetUtils';

export const useResetPassword = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const resetPassword = async (
    token: string,
    newPassword: string,
    confirmPassword: string
  ) => {
    setIsLoading(true);
    setError('');

    // Validate password
    const passwordError = validateNewPassword(newPassword);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return false;
    }

    // Check passwords match
    if (!passwordsMatch(newPassword, confirmPassword)) {
      setError(i18next.t('hooks.resetPassword.passwordsDoNotMatch'));
      setIsLoading(false);
      return false;
    }

    try {
      const response = await fetch('/api/password/reset/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: newPassword,
          confirm_password: confirmPassword,
        } as ResetPasswordRequest),
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to login with success message
        setTimeout(() => {
          navigate('/login', {
            state: { message: i18next.t('hooks.resetPassword.passwordResetSuccess') },
          });
        }, 2000);
        return true;
      } else {
        setError(data.message || i18next.t('hooks.resetPassword.failedToReset'));
        return false;
      }
    } catch (err) {
      setError(i18next.t('hooks.resetPassword.errorOccurred'));
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError('');

  return {
    isLoading,
    error,
    resetPassword,
    clearError,
  };
};
