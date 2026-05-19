import { useState, useEffect } from 'react';
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
        setError('Failed to fetch passwords');
      }
    } catch (err) {
      setError('Error fetching passwords');
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
        setSuccess(`Generated ${data.strength} password`);
        return data.password;
      }
    } catch (err) {
      setError('Failed to generate password: ' + err);
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
        setSuccess(editingId ? 'Password updated successfully' : 'Password created successfully');
        await fetchPasswords();
        return true;
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : (errorData.detail?.[0]?.msg || 'Operation failed');
        setError(errorMessage);
      }
    } catch (err) {
      setError('An error occurred');
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
        setSuccess('Password deleted successfully');
        await fetchPasswords();
        return true;
      } else {
        setError('Failed to delete password');
      }
    } catch (err) {
      setError('Delete operation failed: ' + err);
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
        setError('Failed to decrypt password. Check your master password.');
      }
    } catch (err) {
      setError('Decryption error: ' + err);
    }
    return null;
  };

  const copyPasswordToClipboard = async (password: string): Promise<void> => {
    try {
      await copyToClipboard(password);
      setSuccess('Password copied to clipboard');
    } catch {
      setError('Failed to copy password');
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