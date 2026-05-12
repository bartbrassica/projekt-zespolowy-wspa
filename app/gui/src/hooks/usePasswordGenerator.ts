import { useState } from 'react';
import type { PasswordGeneratorState } from '../types/landing';
import { generateSecurePassword, copyToClipboard } from '../utils/landingUtils';

export const usePasswordGenerator = (): PasswordGeneratorState & {
  generatePassword: () => void;
  copyPassword: () => void;
} => {
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [copied, setCopied] = useState(false);

  const generatePassword = () => {
    const password = generateSecurePassword();
    setGeneratedPassword(password);
  };

  const copyPassword = () => {
    if (generatedPassword) {
      copyToClipboard(generatedPassword);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return {
    generatedPassword,
    copied,
    generatePassword,
    copyPassword
  };
};