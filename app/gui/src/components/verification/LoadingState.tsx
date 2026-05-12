import React from 'react';
import { Loader2 } from 'lucide-react';
import type { LoadingStateProps } from '../../types/verification';

const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Please wait while we verify your email address...'
}) => {
  return (
    <>
      <Loader2 className="h-16 w-16 text-purple-400 animate-spin mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-white mb-2">Verifying Email</h2>
      <p className="text-gray-400">{message}</p>
    </>
  );
};

export default LoadingState;