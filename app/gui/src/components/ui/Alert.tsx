import React from 'react';
import { AlertCircle, Shield } from 'lucide-react';
import type { AlertProps } from '../../types/password';

const Alert: React.FC<AlertProps> = ({ type, message, onClose }) => {
  const isError = type === 'error';

  const bgColor = isError
    ? 'bg-red-50 dark:bg-red-900/20'
    : 'bg-green-50 dark:bg-green-900/20';

  const borderColor = isError ? 'border-red-500' : 'border-green-500';

  const textColor = isError
    ? 'text-red-700 dark:text-red-400'
    : 'text-green-700 dark:text-green-400';

  const iconColor = isError ? 'text-red-500' : 'text-green-500';
  const hoverColor = isError ? 'hover:text-red-700' : 'hover:text-green-700';

  const Icon = isError ? AlertCircle : Shield;

  return (
    <div className={`mb-4 p-4 ${bgColor} border-l-4 ${borderColor} flex items-center gap-3`}>
      <Icon className={`h-5 w-5 ${iconColor}`} />
      <span className={textColor}>{message}</span>
      <button
        onClick={onClose}
        className={`ml-auto ${iconColor} ${hoverColor}`}
      >
        ×
      </button>
    </div>
  );
};

export default Alert;