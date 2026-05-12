export const extractTokenFromUrl = (searchParams: URLSearchParams): string | null => {
  return searchParams.get('token');
};

export const createRedirectDelay = (callback: () => void, delay: number = 3000): ReturnType<typeof setTimeout> => {
  return setTimeout(callback, delay);
};

export const isValidToken = (token: string | null): boolean => {
  return token !== null && token.trim().length > 0;
};

export const getVerificationErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred during verification';
};

export const createNavigationState = (message: string) => ({
  state: { message }
});