export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  phone_number: string;
}

export interface PasswordStrength {
  score: number;
  text: string;
  color: string;
}

export interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface LoginProps {
  onSuccess?: () => void;
}

export interface CheckboxProps {
  id: string;
  name: string;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  className?: string;
}

export interface InputFieldProps {
  id: string;
  name: string;
  type: string;
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  autoComplete?: string;
  icon: React.ReactNode;
  showToggle?: boolean;
  showPassword?: boolean;
  onTogglePassword?: () => void;
  className?: string;
}

// Auth Store Types
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  email: string;
}

export interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  login: (email: string, password: string, remember_me: boolean) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthProviderProps {
  children: React.ReactNode;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me: boolean;
}

export interface StorageService {
  setAuthData: (tokens: AuthTokens, user: User, remember: boolean) => void;
  getAuthData: () => { tokens: AuthTokens; user: User } | null;
  clearAuthData: () => void;
  isTokenExpired: () => boolean;
}

export interface AuthApiService {
  login: (credentials: LoginCredentials) => Promise<AuthTokens>;
  getAccessToken: () => string | null;
  authenticatedFetch: (url: string, options?: RequestInit) => Promise<Response>;
}