import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useEmailVerification } from './hooks';
import { LoadingState, SuccessState, ErrorState } from './components/verification';
import { extractTokenFromUrl } from './utils/verificationUtils';

const EmailVerification: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = extractTokenFromUrl(searchParams);
  const { verificationState, retryVerification } = useEmailVerification(token);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900 bg-opacity-50 backdrop-blur-xl rounded-2xl p-8 border border-gray-800 shadow-2xl text-center">
        {verificationState.status === 'loading' && <LoadingState />}

        {verificationState.status === 'success' && (
          <SuccessState message={verificationState.message} />
        )}

        {verificationState.status === 'error' && (
          <ErrorState
            message={verificationState.message}
            onRetry={token ? retryVerification : undefined}
          />
        )}
      </div>
    </div>
  );
};

export default EmailVerification;
