import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import i18next from 'i18next';
import type { VerificationState, VerificationResponse } from '../types/verification';

export const useEmailVerification = (token: string | null) => {
  const navigate = useNavigate();
  const [verificationState, setVerificationState] = useState<VerificationState>({
    status: 'loading',
    message: ''
  });

  const verifyEmail = async (verificationToken: string): Promise<VerificationResponse> => {
    try {
      const response = await fetch('/api/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: verificationToken }),
      });

      const data = await response.json();

      if (response.ok) {
        return {
          success: true,
          message: data.message || i18next.t('hooks.emailVerification.emailVerifiedSuccess')
        };
      } else {
        return {
          success: false,
          message: data.message || i18next.t('hooks.emailVerification.verificationFailed')
        };
      }
    } catch {
      return {
        success: false,
        message: i18next.t('hooks.emailVerification.errorDuringVerification')
      };
    }
  };

  const handleVerification = useCallback(async () => {
    if (!token) {
      setVerificationState({
        status: 'error',
        message: i18next.t('hooks.emailVerification.noTokenProvided')
      });
      return;
    }

    setVerificationState({
      status: 'loading',
      message: ''
    });

    const result = await verifyEmail(token);

    if (result.success) {
      setVerificationState({
        status: 'success',
        message: result.message || i18next.t('hooks.emailVerification.emailVerified')
      });

      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login', {
          state: { message: i18next.t('hooks.emailVerification.emailVerifiedSignIn') }
        });
      }, 3000);
    } else {
      setVerificationState({
        status: 'error',
        message: result.message || i18next.t('hooks.emailVerification.verificationFailed')
      });
    }
  }, [token, navigate]);

  const retryVerification = () => {
    handleVerification();
  };

  useEffect(() => {
    handleVerification();
  }, [token, handleVerification]);

  return {
    verificationState,
    retryVerification
  };
};