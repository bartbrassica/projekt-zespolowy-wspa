import { useState, useEffect } from 'react';
import type { PasswordStrengthState } from '../types/landing';
import { calculatePasswordStrength } from '../utils/landingUtils';

export const usePasswordStrengthDemo = (): PasswordStrengthState & {
  handlePasswordChange: (password: string) => void;
} => {
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);

  useEffect(() => {
    setPasswordStrength(calculatePasswordStrength(passwordInput));
  }, [passwordInput]);

  const handlePasswordChange = (password: string) => {
    setPasswordInput(password);
  };

  return {
    passwordInput,
    passwordStrength,
    handlePasswordChange
  };
};