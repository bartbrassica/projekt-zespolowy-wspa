import { useState } from 'react';

export const usePasswordVisibility = () => {
  const [showPassword, setShowPassword] = useState<{ [key: string]: boolean }>({});
  const [decryptedPasswords, setDecryptedPasswords] = useState<{ [key: string]: string }>({});

  const toggleVisibility = (entryId: string) => {
    setShowPassword(prev => ({ ...prev, [entryId]: !prev[entryId] }));
  };

  const showPasswordForEntry = (entryId: string) => {
    setShowPassword(prev => ({ ...prev, [entryId]: true }));
  };

  const hidePasswordForEntry = (entryId: string) => {
    setShowPassword(prev => ({ ...prev, [entryId]: false }));
  };

  const setDecryptedPassword = (entryId: string, password: string) => {
    setDecryptedPasswords(prev => ({ ...prev, [entryId]: password }));
  };

  const getDecryptedPassword = (entryId: string): string | undefined => {
    return decryptedPasswords[entryId];
  };

  const isPasswordVisible = (entryId: string): boolean => {
    return !!showPassword[entryId];
  };

  const clearDecryptedPassword = (entryId: string) => {
    setDecryptedPasswords(prev => {
      const newState = { ...prev };
      delete newState[entryId];
      return newState;
    });
  };

  return {
    showPassword,
    decryptedPasswords,
    toggleVisibility,
    showPasswordForEntry,
    hidePasswordForEntry,
    setDecryptedPassword,
    getDecryptedPassword,
    isPasswordVisible,
    clearDecryptedPassword
  };
};