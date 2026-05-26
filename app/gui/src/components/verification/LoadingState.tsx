import React from 'react';
import { Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { LoadingStateProps } from '../../types/verification';

const LoadingState: React.FC<LoadingStateProps> = ({ message }) => {
  const { t } = useTranslation();
  const displayMessage = message || t('emailVerification.defaultLoadingMessage');

  return (
    <>
      <Loader2 className="h-16 w-16 text-purple-400 animate-spin mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-white mb-2">{t('emailVerification.verifyingEmail')}</h2>
      <p className="text-gray-400">{displayMessage}</p>
    </>
  );
};

export default LoadingState;