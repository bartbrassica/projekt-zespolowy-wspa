import React from 'react';
import { CheckCircle } from 'lucide-react';
import type { SuccessStateProps } from '../../types/verification';

const SuccessState: React.FC<SuccessStateProps> = ({
  message,
  redirectMessage = 'Redirecting to login page...'
}) => {
  return (
    <>
      <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-white mb-2">Email Verified!</h2>
      <p className="text-gray-400 mb-4">{message}</p>
      <p className="text-sm text-gray-500">{redirectMessage}</p>
    </>
  );
};

export default SuccessState;