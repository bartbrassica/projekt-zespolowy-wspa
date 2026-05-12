import type { LoginCredentials, AuthTokens } from '../types/auth';

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
  }
};