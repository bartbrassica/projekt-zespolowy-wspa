import { useState } from 'react';
import { authApi } from '../services/authApi';
import type { ShareLinkFormData, ShareLink } from '../types/password';

export const useShareLinks = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdLink, setCreatedLink] = useState<ShareLink | null>(null);

  const createShareLink = async (formData: ShareLinkFormData): Promise<ShareLink | null> => {
    try {
      setLoading(true);
      setError(null);
      const shareLink = await authApi.createShareLink(formData);
      setCreatedLink(shareLink);
      return shareLink;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create share link';
      setError(errorMessage);
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);
  const clearCreatedLink = () => setCreatedLink(null);

  return {
    loading,
    error,
    createdLink,
    createShareLink,
    clearError,
    clearCreatedLink
  };
};
