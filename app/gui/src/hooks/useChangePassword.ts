import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import i18next from 'i18next';
import type { ChangePasswordRequest } from '../types/password-reset';
import { validateNewPassword, passwordsMatch } from '../utils/passwordResetUtils';
import { authApi } from '../services/authApi';

export const useChangePassword = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const changePassword = async (
    currentPassword: string,
    newPassword: string,
    confirmPassword: string
  ) => {
    setIsLoading(true);
    setError('');
    setSuccess(false);

    // Validate new password
    const passwordError = validateNewPassword(newPassword);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return false;
    }

    // Check passwords match
    if (!passwordsMatch(newPassword, confirmPassword)) {
      setError(i18next.t('hooks.changePassword.passwordsDoNotMatch'));
      setIsLoading(false);
      return false;
    }

    // Check new password is different from current
    if (currentPassword === newPassword) {
      setError(i18next.t('hooks.changePassword.newPasswordMustBeDifferent'));
      setIsLoading(false);
      return false;
    }

    try {
      const token = authApi.getAccessToken();
      if (!token) {
        setError(i18next.t('hooks.changePassword.authenticationRequired'));
        navigate('/login');
        return false;
      }

      const response = await fetch('/api/password/change', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        } as ChangePasswordRequest),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Log out user and redirect to login after password change
        setTimeout(() => {
          localStorage.clear();
          sessionStorage.clear();
          navigate('/login', {
            state: { message: i18next.t('hooks.changePassword.passwordChangedSuccess') },
          });
        }, 2000);
        return true;
      } else {
        setError(data.message || i18next.t('hooks.changePassword.failedToChange'));
        return false;
      }
    } catch (err) {
      setError(i18next.t('hooks.changePassword.errorOccurred'));
      return false;
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
    changePassword,
    clearError,
    clearSuccess,
  };
};
