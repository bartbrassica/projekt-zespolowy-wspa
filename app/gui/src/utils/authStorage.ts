import type { AuthTokens, User } from '../types/auth';

export const authStorage = {
  setAuthData(tokens: AuthTokens, user: User, remember: boolean): void {
    if (remember) {
      localStorage.setItem('auth_tokens', JSON.stringify(tokens));
      localStorage.setItem('user', JSON.stringify(user));

      // Calculate and store token expiry time
      const expiryTime = new Date().getTime() + (tokens.expires_in * 1000);
      localStorage.setItem('token_expiry', expiryTime.toString());
    } else {
      // Store in session storage for current session only
      sessionStorage.setItem('auth_tokens', JSON.stringify(tokens));
      sessionStorage.setItem('user', JSON.stringify(user));
    }
  },

  getAuthData(): { tokens: AuthTokens; user: User } | null {
    const storedTokens = localStorage.getItem('auth_tokens') || sessionStorage.getItem('auth_tokens');
    const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');

    if (storedTokens && storedUser) {
      try {
        const tokens = JSON.parse(storedTokens);
        const user = JSON.parse(storedUser);

        // Check if token is expired (only for localStorage)
        if (localStorage.getItem('auth_tokens') && this.isTokenExpired()) {
          this.clearAuthData();
          return null;
        }

        return { tokens, user };
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        this.clearAuthData();
        return null;
      }
    }

    return null;
  },

  clearAuthData(): void {
    // Clear all storage
    localStorage.removeItem('auth_tokens');
    localStorage.removeItem('user');
    localStorage.removeItem('token_expiry');
    sessionStorage.removeItem('auth_tokens');
    sessionStorage.removeItem('user');
  },

  isTokenExpired(): boolean {
    const tokenExpiry = localStorage.getItem('token_expiry');
    if (!tokenExpiry) {
      return false;
    }

    return new Date().getTime() >= parseInt(tokenExpiry);
  }
};