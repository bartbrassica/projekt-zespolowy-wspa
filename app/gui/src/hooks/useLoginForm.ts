import { useState } from 'react';
import type { LoginFormData } from '../types/auth';

export const useLoginForm = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, email: e.target.value }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, password: e.target.value }));
  };

  const handleRememberMeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, rememberMe: e.target.checked }));
  };

  const clearError = () => setError('');

  const isFormValid = (): boolean => {
    return formData.email.trim() !== '' && formData.password.trim() !== '';
  };

  return {
    formData,
    showPassword,
    setShowPassword,
    error,
    setError,
    handleEmailChange,
    handlePasswordChange,
    handleRememberMeChange,
    clearError,
    isFormValid
  };
};