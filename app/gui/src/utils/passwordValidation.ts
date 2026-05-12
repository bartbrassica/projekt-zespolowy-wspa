import type { PasswordStrength } from '../types/auth';

export const calculatePasswordStrength = (password: string): number => {
  let strength = 0;
  if (password.length >= 8) strength += 20;
  if (password.length >= 12) strength += 20;
  if (/[a-z]/.test(password)) strength += 15;
  if (/[A-Z]/.test(password)) strength += 15;
  if (/[0-9]/.test(password)) strength += 15;
  if (/[^A-Za-z0-9]/.test(password)) strength += 15;
  return strength;
};

export const getPasswordStrength = (password: string): PasswordStrength => {
  const score = calculatePasswordStrength(password);

  if (score < 40) {
    return {
      score,
      text: 'Weak',
      color: 'from-red-500 to-red-600'
    };
  }

  if (score < 70) {
    return {
      score,
      text: 'Medium',
      color: 'from-yellow-500 to-yellow-600'
    };
  }

  return {
    score,
    text: 'Strong',
    color: 'from-green-500 to-green-600'
  };
};

export const validatePasswordMatch = (password: string, confirmPassword: string): boolean => {
  return password === confirmPassword;
};

export const isPasswordStrong = (password: string): boolean => {
  return calculatePasswordStrength(password) >= 40;
};