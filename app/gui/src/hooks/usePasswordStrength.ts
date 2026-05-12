import { useMemo } from 'react';
import { getPasswordStrength } from '../utils/passwordValidation';
import type { PasswordStrength } from '../types/auth';

export const usePasswordStrength = (password: string): PasswordStrength => {
  return useMemo(() => getPasswordStrength(password), [password]);
};