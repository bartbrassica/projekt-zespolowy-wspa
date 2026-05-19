import { useState, useEffect } from 'react';
import { authApi } from '../services/authApi';
import type { Tag } from '../types/password';

export const useTagManager = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      setLoading(true);
      const data = await authApi.fetchTags();
      setTags(data);
      setError(null);
    } catch (err) {
      setError('Error fetching tags');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createTag = async (name: string, color?: string): Promise<Tag | null> => {
    try {
      const tag = await authApi.createTag(name, color);
      await fetchTags();
      return tag;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create tag';
      setError(errorMessage);
      console.error(err);
      return null;
    }
  };

  const deleteTag = async (tagId: string): Promise<boolean> => {
    try {
      await authApi.deleteTag(tagId);
      await fetchTags();
      return true;
    } catch (err) {
      setError('Error deleting tag');
      console.error(err);
      return false;
    }
  };

  const clearError = () => setError(null);

  return {
    tags,
    loading,
    error,
    fetchTags,
    createTag,
    deleteTag,
    clearError
  };
};
