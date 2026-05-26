import { useState, useEffect } from 'react';
import i18next from 'i18next';
import { authApi } from '../services/authApi';
import type { PasswordEntry, PasswordGeneratorSettings, PasswordFormData, Tag } from '../types/password';
import { copyToClipboard, createPayloadFromFormData } from '../utils/passwordUtils';

export const usePasswordManager = () => {
  const [passwords, setPasswords] = useState<PasswordEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const generatorSettings: PasswordGeneratorSettings = {
    length: 16,
    include_symbols: true,
    include_numbers: true,
    include_uppercase: true,
    include_lowercase: true,
    exclude_ambiguous: true
  };

  useEffect(() => {
    fetchPasswords();
  }, []);

  const fetchPasswords = async () => {
    try {
      setLoading(true);
      const response = await authApi.authenticatedFetch('/api/passwords/entries');
      if (response.ok) {
        const data = await response.json();
        setPasswords(data);
      } else {
        setError(i18next.t('hooks.passwordManager.failedToFetch'));
      }
    } catch (err) {
      setError(i18next.t('hooks.passwordManager.errorFetching'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generatePassword = async (): Promise<string | null> => {
    try {
      const response = await fetch('/api/passwords/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatorSettings)
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(i18next.t('hooks.passwordManager.generatedPassword', { strength: data.strength }));
        return data.password;
      }
    } catch (err) {
      setError(i18next.t('hooks.passwordManager.failedToGenerate') + err);
    }
    return null;
  };

  const savePassword = async (formData: PasswordFormData, editingId: string | null, allTags?: Tag[]): Promise<boolean> => {
    try {
      const url = editingId
        ? `/api/passwords/entries/${editingId}`
        : '/api/passwords/entries';

      const method = editingId ? 'PUT' : 'POST';
      const payload = createPayloadFromFormData(formData, editingId, allTags);

      const response = await authApi.authenticatedFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSuccess(editingId ? i18next.t('hooks.passwordManager.passwordUpdated') : i18next.t('hooks.passwordManager.passwordCreated'));
        await fetchPasswords();
        return true;
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : (errorData.detail?.[0]?.msg || i18next.t('hooks.passwordManager.operationFailed'));
        setError(errorMessage);
      }
    } catch (err) {
      setError(i18next.t('hooks.passwordManager.errorOccurred'));
      console.error(err);
    }
    return false;
  };

  const deletePassword = async (entryId: string, masterPassword: string): Promise<boolean> => {
    try {
      const response = await authApi.authenticatedFetch(`/api/passwords/entries/${entryId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ master_password: masterPassword })
      });

      if (response.ok) {
        setSuccess(i18next.t('hooks.passwordManager.passwordDeleted'));
        await fetchPasswords();
        return true;
      } else {
        setError(i18next.t('hooks.passwordManager.failedToDelete'));
      }
    } catch (err) {
      setError(i18next.t('hooks.passwordManager.deleteOperationFailed') + err);
    }
    return false;
  };

  const toggleFavorite = async (entry: PasswordEntry, masterPassword: string): Promise<void> => {
    try {
      const response = await authApi.authenticatedFetch(`/api/passwords/entries/${entry.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_favorite: !entry.is_favorite,
          master_password: masterPassword
        })
      });

      if (response.ok) {
        await fetchPasswords();
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const decryptPassword = async (entryId: string, masterPassword: string): Promise<string | null> => {
    try {
      const response = await authApi.authenticatedFetch(`/api/passwords/entries/${entryId}/decrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ master_password: masterPassword })
      });

      if (response.ok) {
        const data = await response.json();
        return data.password;
      } else {
        setError(i18next.t('hooks.passwordManager.failedToDecrypt'));
      }
    } catch (err) {
      setError(i18next.t('hooks.passwordManager.decryptionError') + err);
    }
    return null;
  };

  const copyPasswordToClipboard = async (password: string): Promise<void> => {
    try {
      await copyToClipboard(password);
      setSuccess(i18next.t('hooks.passwordManager.passwordCopied'));
    } catch {
      setError(i18next.t('hooks.passwordManager.failedToCopy'));
    }
  };

  const clearError = () => setError(null);
  const clearSuccess = () => setSuccess(null);

  return {
    passwords,
    loading,
    error,
    success,
    fetchPasswords,
    generatePassword,
    savePassword,
    deletePassword,
    toggleFavorite,
    decryptPassword,
    copyPasswordToClipboard,
    clearError,
    clearSuccess
  };
};