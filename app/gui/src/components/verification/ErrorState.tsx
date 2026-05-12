import React from 'react';
import { XCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { ErrorStateProps } from '../../types/verification';

const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => {
  return (
    <>
      <XCircle className="h-16 w-16 text-red-400 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-white mb-2">Verification Failed</h2>
      <p className="text-gray-400 mb-6">{message}</p>
      <div className="space-y-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className="block w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-300"
          >
            Try Again
          </button>
        )}
        <Link
          to="/login"
          className="block w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-all duration-300"
        >
          Go to Login
        </Link>
        <Link
          to="/register"
          className="block w-full bg-gray-700 text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-600 transition-all duration-300"
        >
          Register Again
        </Link>
      </div>
    </>
  );
};

export default ErrorState;