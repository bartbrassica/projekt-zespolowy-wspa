import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Lock, CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useResetPassword } from './hooks/useResetPassword';
import { usePasswordStrength } from './hooks/usePasswordStrength';
import { extractResetToken } from './utils/passwordResetUtils';
import { InputField, ErrorMessage, LoadingButton, PasswordStrengthIndicator, LanguageSwitcher } from './components/ui';

const ResetPassword: React.FC = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = extractResetToken(searchParams);
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const { isLoading, error, resetPassword } = useResetPassword();
  const passwordStrength = usePasswordStrength(newPassword);

  useEffect(() => {
    if (!token) {
      // Token is missing
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!token) {
      return;
    }

    const success = await resetPassword(token, newPassword, confirmPassword);
    if (success) {
      setResetSuccess(true);
    }
  };

  const isFormValid = () => {
    return newPassword.length >= 8 && 
           confirmPassword.length >= 8 && 
           newPassword === confirmPassword;
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-black text-white relative overflow-hidden flex items-center justify-center">
        <div className="bg-gray-900 bg-opacity-50 backdrop-blur-xl rounded-2xl p-8 border border-gray-800 shadow-2xl max-w-md">
          <h2 className="text-2xl font-bold text-red-400 mb-4">{t('resetPassword.invalidLinkTitle')}</h2>
          <p className="text-gray-400 mb-6">
            {t('resetPassword.invalidLinkMessage')}
          </p>
          <Link
            to="/forgot-password"
            className="inline-block w-full text-center px-4 py-3 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-md font-semibold hover:scale-105 transition-all"
          >
            {t('resetPassword.requestNewLink')}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 opacity-30 overflow-hidden pointer-events-none">
        <div 
          className="absolute inset-[-20%] bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-600 animate-pulse"
          style={{
            background: 'radial-gradient(circle at center, rgba(147, 51, 234, 0.3) 0%, rgba(59, 130, 246, 0.3) 50%, rgba(6, 182, 212, 0.3) 100%)'
          }}
        ></div>
        <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      </div>

      {/* Navigation Bar */}
      <nav className="relative z-50 w-full">
        <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24 py-4 md:py-6 lg:py-8">
          <Link to="/" className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent hover:scale-105 transition-transform">
            {t('common.brandName')}
          </Link>
          <LanguageSwitcher />
        </div>
      </nav>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-20">
        <div className="w-full max-w-md px-4 sm:px-6 lg:px-8">
          <div className="bg-gray-900 bg-opacity-50 backdrop-blur-xl rounded-2xl p-8 border border-gray-800 shadow-2xl">
            {resetSuccess ? (
              <div className="flex flex-col items-center justify-center text-center space-y-4">
                <div className="rounded-full bg-green-500/20 p-3">
                  <CheckCircle className="h-12 w-12 text-green-400" />
                </div>
                <h3 className="text-xl font-semibold text-white">{t('resetPassword.successTitle')}</h3>
                <p className="text-gray-400">
                  {t('resetPassword.successMessage')}
                </p>
              </div>
            ) : (
              <>
                <div>
                  <h2 className="text-center text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                    {t('resetPassword.title')}
                  </h2>
                  <p className="mt-2 text-center text-sm text-gray-400">
                    {t('resetPassword.subtitle')}
                  </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                  <div>
                    <InputField
                      id="new-password"
                      name="newPassword"
                      type="password"
                      placeholder={t('resetPassword.newPasswordPlaceholder')}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                      autoComplete="new-password"
                      icon={<Lock className="h-5 w-5 text-gray-400" />}
                      showToggle
                      showPassword={showNewPassword}
                      onTogglePassword={() => setShowNewPassword(!showNewPassword)}
                      className="appearance-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                    />
                    <PasswordStrengthIndicator strength={passwordStrength} password={newPassword} />
                  </div>

                  <div>
                    <InputField
                      id="confirm-password"
                      name="confirmPassword"
                      type="password"
                      placeholder={t('resetPassword.confirmPasswordPlaceholder')}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      autoComplete="new-password"
                      icon={<Lock className="h-5 w-5 text-gray-400" />}
                      showToggle
                      showPassword={showConfirmPassword}
                      onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="appearance-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                    />
                    {confirmPassword && newPassword !== confirmPassword && (
                      <p className="mt-1 text-xs text-red-400">{t('register.passwordMismatch')}</p>
                    )}
                  </div>

                  <ErrorMessage message={error} />

                  <div>
                    <LoadingButton
                      type="submit"
                      isLoading={isLoading}
                      disabled={!isFormValid()}
                      loadingText={t('resetPassword.resettingPassword')}
                    >
                      {t('resetPassword.resetPasswordButton')}
                    </LoadingButton>
                  </div>

                  <div className="text-center">
                    <span className="text-sm text-gray-400">
                      {t('resetPassword.rememberPassword')}{' '}
                      <Link to="/login" className="font-medium text-purple-400 hover:text-purple-300">
                        {t('login.signInButton')}
                      </Link>
                    </span>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
