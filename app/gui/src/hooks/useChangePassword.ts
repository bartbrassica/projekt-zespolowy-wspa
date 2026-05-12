import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
      setError('Passwords do not match');
      setIsLoading(false);
      return false;
    }

    // Check new password is different from current
    if (currentPassword === newPassword) {
      setError('New password must be different from current password');
      setIsLoading(false);
      return false;
    }

    try {
      const token = authApi.getAccessToken();
      if (!token) {
        setError('Authentication required');
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
            state: { message: 'Password changed successfully! Please sign in with your new password.' },
          });
        }, 2000);
        return true;
      } else {
        setError(data.message || 'Failed to change password');
        return false;
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
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
