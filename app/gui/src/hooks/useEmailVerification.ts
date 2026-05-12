import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
          message: data.message || 'Your email has been successfully verified!'
        };
      } else {
        return {
          success: false,
          message: data.message || 'Verification failed'
        };
      }
    } catch {
      return {
        success: false,
        message: 'An error occurred during verification'
      };
    }
  };

  const handleVerification = useCallback(async () => {
    if (!token) {
      setVerificationState({
        status: 'error',
        message: 'No verification token provided'
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
        message: result.message || 'Email verified successfully!'
      });

      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login', {
          state: { message: 'Email verified! Please sign in to continue.' }
        });
      }, 3000);
    } else {
      setVerificationState({
        status: 'error',
        message: result.message || 'Verification failed'
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