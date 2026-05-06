import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  login: (email: string, password: string, remember_me: boolean) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for stored tokens on mount
  useEffect(() => {
    const storedTokens = localStorage.getItem('auth_tokens');
    const storedUser = localStorage.getItem('user');
    
    if (storedTokens && storedUser) {
      try {
        const parsedTokens = JSON.parse(storedTokens);
        const parsedUser = JSON.parse(storedUser);
        
        // Check if token is expired
        const tokenExpiry = localStorage.getItem('token_expiry');
        if (tokenExpiry && new Date().getTime() < parseInt(tokenExpiry)) {
          setTokens(parsedTokens);
          setUser(parsedUser);
        } else {
          // Clear expired tokens
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('user');
          localStorage.removeItem('token_expiry');
        }
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
      }
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string, remember_me: boolean) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          remember_me,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Login failed');
      }

      const data: AuthTokens = await response.json();
      
      setTokens(data);
      setUser({ email });

      // Store tokens if remember_me is true
      if (remember_me) {
        localStorage.setItem('auth_tokens', JSON.stringify(data));
        localStorage.setItem('user', JSON.stringify({ email }));
        
        // Calculate and store token expiry time
        const expiryTime = new Date().getTime() + (data.expires_in * 1000);
        localStorage.setItem('token_expiry', expiryTime.toString());
      } else {
        // Store in session storage for current session only
        sessionStorage.setItem('auth_tokens', JSON.stringify(data));
        sessionStorage.setItem('user', JSON.stringify({ email }));
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setTokens(null);
    
    // Clear all storage
    localStorage.removeItem('auth_tokens');
    localStorage.removeItem('user');
    localStorage.removeItem('token_expiry');
    sessionStorage.removeItem('auth_tokens');
    sessionStorage.removeItem('user');
  };

  const value = {
    user,
    tokens,
    login,
    logout,
    isAuthenticated: !!user && !!tokens,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Export helper functions
// eslint-disable-next-line react-refresh/only-export-components
export const getAccessToken = (): string | null => {
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
};

// eslint-disable-next-line react-refresh/only-export-components
export const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
  const token = getAccessToken();
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
};
