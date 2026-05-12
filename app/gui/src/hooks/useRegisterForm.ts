import { useState } from 'react';
import type { RegisterFormData } from '../types/auth';
import { validatePasswordMatch, isPasswordStrong } from '../utils/passwordValidation';

export const useRegisterForm = () => {
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone_number: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = (): string | null => {
    if (!validatePasswordMatch(formData.password, formData.confirmPassword)) {
      return 'Passwords do not match';
    }

    if (!isPasswordStrong(formData.password)) {
      return 'Please choose a stronger password';
    }

    return null;
  };

  const isFormValid = (): boolean => {
    return validatePasswordMatch(formData.password, formData.confirmPassword) &&
           isPasswordStrong(formData.password);
  };

  const clearError = () => setError('');

  return {
    formData,
    showPassword,
    setShowPassword,
    showConfirmPassword,
    setShowConfirmPassword,
    isLoading,
    setIsLoading,
    error,
    setError,
    handleChange,
    validateForm,
    isFormValid,
    clearError
  };
};