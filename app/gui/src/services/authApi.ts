import type { LoginCredentials, AuthTokens } from '../types/auth';
import type { Tag, ShareLinkFormData, ShareLink, SharedPasswordData } from '../types/password';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Login failed');
    }

    return response.json();
  },

  getAccessToken(): string | null {
    const tokens = localStorage.getItem('auth_tokens') || sessionStorage.getItem('auth_tokens');
    if (tokens) {
      try {
        const parsed = JSON.parse(tokens);
        return parsed.access_token;
      } catch {
        return null;
      }
    }
    return null;
  },

  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = authApi.getAccessToken();
    if (!token) {
      throw new Error('No authentication token available');
    }

    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  // Tag management
  async fetchTags(): Promise<Tag[]> {
    const response = await authApi.authenticatedFetch('/api/passwords/tags');
    if (!response.ok) {
      throw new Error('Failed to fetch tags');
    }
    return response.json();
  },

  async createTag(name: string, color?: string): Promise<Tag> {
    const response = await authApi.authenticatedFetch('/api/passwords/tags', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, color }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Failed to create tag');
    }
    return response.json();
  },

  async deleteTag(tagId: string): Promise<void> {
    const response = await authApi.authenticatedFetch(`/api/passwords/tags/${tagId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete tag');
    }
  },

  // Share link management
  async createShareLink(formData: ShareLinkFormData): Promise<ShareLink> {
    const response = await authApi.authenticatedFetch('/api/passwords/share', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Failed to create share link');
    }
    return response.json();
  },

  async getSharedPassword(shareToken: string): Promise<SharedPasswordData> {
    // Public endpoint - no authentication required
    const response = await fetch(`/api/passwords/shared/${shareToken}`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Failed to access shared password');
    }
    return response.json();
  },

  // Export passwords
  async exportPasswords(masterPassword: string, format: 'csv' | 'json' | 'xlsx' = 'xlsx', includePasswords: boolean = true): Promise<{ format: string; data: string; filename: string }> {
    const response = await authApi.authenticatedFetch('/api/passwords/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        format,
        master_password: masterPassword,
        include_passwords: includePasswords,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Failed to export passwords');
    }
    return response.json();
  },

  // Import passwords
  async importPasswords(masterPassword: string, fileData: string, format: 'csv' | 'json' | 'xlsx' = 'xlsx'): Promise<{ message: string }> {
    const response = await authApi.authenticatedFetch('/api/passwords/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        format,
        master_password: masterPassword,
        data: fileData,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || 'Failed to import passwords');
    }
    return response.json();
  }
};