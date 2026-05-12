import React from 'react';

interface ErrorMessageProps {
  message: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div className="rounded-md bg-red-900 bg-opacity-20 backdrop-blur p-4 border border-red-800">
      <div className="flex">
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-400">Error</h3>
          <div className="mt-2 text-sm text-red-300">
            <p>{message}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;