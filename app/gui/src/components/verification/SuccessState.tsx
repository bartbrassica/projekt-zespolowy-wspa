import React from 'react';
import { CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { SuccessStateProps } from '../../types/verification';

const SuccessState: React.FC<SuccessStateProps> = ({ message, redirectMessage }) => {
  const { t } = useTranslation();
  const displayRedirectMessage = redirectMessage || t('emailVerification.redirectingToLogin');

  return (
    <>
      <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-white mb-2">{t('emailVerification.emailVerified')}</h2>
      <p className="text-gray-400 mb-4">{message}</p>
      <p className="text-sm text-gray-500">{displayRedirectMessage}</p>
    </>
  );
};

export default SuccessState;