import { useState, useEffect } from 'react';
import { authApi } from '../services/authApi';
import type { Folder } from '../types/password';

export const useFolderManager = () => {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFolders();
  }, []);

  const fetchFolders = async () => {
    try {
      setLoading(true);
      const response = await authApi.authenticatedFetch('/api/passwords/folders');
      if (response.ok) {
        const data = await response.json();
        setFolders(data);
      } else {
        setError('Failed to fetch folders');
      }
    } catch (err) {
      setError('Error fetching folders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createFolder = async (name: string, parentId?: string, icon?: string, color?: string): Promise<Folder | null> => {
    try {
      const payload: any = {
        name,
        parent_id: parentId || null
      };

      // Only include icon and color if they have valid values
      if (icon && icon.trim()) {
        payload.icon = icon;
      }
      if (color && color.match(/^#[0-9A-Fa-f]{6}$/)) {
        payload.color = color;
      }

      const response = await authApi.authenticatedFetch('/api/passwords/folders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const folder = await response.json();
        await fetchFolders();
        return folder;
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : (errorData.detail?.[0]?.msg || 'Failed to create folder');
        setError(errorMessage);
      }
    } catch (err) {
      setError('Error creating folder');
      console.error(err);
    }
    return null;
  };

  const updateFolder = async (folderId: string, updates: Partial<Omit<Folder, 'id' | 'entry_count' | 'created_at' | 'updated_at'>>): Promise<boolean> => {
    try {
      const response = await authApi.authenticatedFetch(`/api/passwords/folders/${folderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        await fetchFolders();
        return true;
      } else {
        setError('Failed to update folder');
      }
    } catch (err) {
      setError('Error updating folder');
      console.error(err);
    }
    return false;
  };

  const deleteFolder = async (folderId: string): Promise<boolean> => {
    try {
      const response = await authApi.authenticatedFetch(`/api/passwords/folders/${folderId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchFolders();
        return true;
      } else {
        setError('Failed to delete folder');
      }
    } catch (err) {
      setError('Error deleting folder');
      console.error(err);
    }
    return false;
  };

  const clearError = () => setError(null);

  return {
    folders,
    loading,
    error,
    fetchFolders,
    createFolder,
    updateFolder,
    deleteFolder,
    clearError
  };
};
