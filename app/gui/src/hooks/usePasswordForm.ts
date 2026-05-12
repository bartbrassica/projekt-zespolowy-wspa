import { useState } from 'react';
import type { PasswordFormData, PasswordEntry } from '../types/password';
import { resetFormData } from '../utils/passwordUtils';

export const usePasswordForm = () => {
  const [formData, setFormData] = useState<PasswordFormData>(resetFormData());
  const [showPassword, setShowPassword] = useState<{ [key: string]: boolean }>({});

  const updateFormData = (updates: Partial<PasswordFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const resetForm = (masterPassword: string = '') => {
    setFormData(resetFormData(masterPassword));
  };

  const loadEntryIntoForm = (entry: PasswordEntry, masterPassword: string) => {
    setFormData({
      name: entry.name,
      site: entry.site,
      username: entry.username,
      password: '',
      notes: entry.notes,
      is_favorite: entry.is_favorite,
      expires_at: entry.expires_at
        ? new Date(entry.expires_at).toISOString().slice(0, 10)
        : '',
      master_password: masterPassword
    });
  };

  const togglePasswordVisibility = (key: string) => {
    setShowPassword(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const updatePassword = (password: string) => {
    setFormData(prev => ({ ...prev, password }));
  };

  return {
    formData,
    updateFormData,
    resetForm,
    loadEntryIntoForm,
    showPassword,
    togglePasswordVisibility,
    updatePassword
  };
};