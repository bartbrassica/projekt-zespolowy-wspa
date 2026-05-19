import type { PasswordEntry, PasswordStrengthInfo, PasswordFormData, Tag } from '../types/password';

export const getPasswordStrength = (password: string): PasswordStrengthInfo => {
  if (!password) return { strength: 'None', color: 'text-gray-400' };
  if (password.length < 8) return { strength: 'Weak', color: 'text-red-500' };
  if (password.length < 12) return { strength: 'Medium', color: 'text-yellow-500' };
  return { strength: 'Strong', color: 'text-green-500' };
};

export const filterPasswords = (passwords: PasswordEntry[], searchQuery: string): PasswordEntry[] => {
  return passwords
    .filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.site.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.username.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      // Sort favorites first
      if (a.is_favorite && !b.is_favorite) return -1;
      if (!a.is_favorite && b.is_favorite) return 1;
      return 0;
    });
};

export const getSiteHostname = (url: string): string => {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
};

export const copyToClipboard = async (text: string): Promise<void> => {
  await navigator.clipboard.writeText(text);

  // Auto-clear clipboard after 30 seconds
  setTimeout(() => {
    navigator.clipboard.writeText('');
  }, 30000);
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString();
};

export const resetFormData = (masterPassword: string = '') => ({
  name: '',
  site: '',
  username: '',
  password: '',
  notes: '',
  expires_at: '',
  is_favorite: false,
  master_password: masterPassword
});

export const createPayloadFromFormData = (formData: PasswordFormData, editingId: string | null, allTags?: Tag[]) => {
  const payload: Record<string, string | boolean | string[] | null> = {
    name: formData.name,
    site: formData.site,
    username: formData.username,
    notes: formData.notes,
    is_favorite: formData.is_favorite,
    master_password: formData.master_password,
    expires_at: formData.expires_at
      ? new Date(formData.expires_at).toISOString()
      : null
  };

  if (formData.password || !editingId) {
    payload.password = formData.password;
  }

  if (formData.folder_id) {
    payload.folder_id = formData.folder_id;
  }

  // Convert tag IDs to tag names for API
  if (formData.tag_ids && formData.tag_ids.length > 0 && allTags) {
    const tagNames = formData.tag_ids
      .map(tagId => {
        const tag = allTags.find(t => t.id === tagId);
        return tag?.name;
      })
      .filter((name): name is string => typeof name === 'string');
    if (tagNames.length > 0) {
      payload.tags = tagNames;
    }
  } else if (formData.tag_ids && formData.tag_ids.length === 0) {
    // Explicitly set empty tags array if no tags selected
    payload.tags = [];
  }

  return payload;
};