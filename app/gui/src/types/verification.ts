export type VerificationStatus = 'loading' | 'success' | 'error';

export interface VerificationState {
  status: VerificationStatus;
  message: string;
}

export interface LoadingStateProps {
  message?: string;
}

export interface SuccessStateProps {
  message: string;
  redirectMessage?: string;
}

export interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export interface VerificationResponse {
  success: boolean;
  message?: string;
}