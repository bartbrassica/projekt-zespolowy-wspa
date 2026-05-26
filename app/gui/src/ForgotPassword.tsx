import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useForgotPassword } from './hooks/useForgotPassword';
import { validateEmail } from './utils/passwordResetUtils';
import { InputField, ErrorMessage, LoadingButton, LanguageSwitcher } from './components/ui';

const ForgotPassword: React.FC = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const { isLoading, error, success, requestPasswordReset } = useForgotPassword();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateEmail(email)) {
      return;
    }

    await requestPasswordReset(email);
  };

  const isFormValid = () => {
    return email.trim() !== '' && validateEmail(email);
  };

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
            {/* Back to Login Link */}
            <Link
              to="/login"
              className="inline-flex items-center text-sm text-gray-400 hover:text-white transition-colors mb-6"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              {t('forgotPassword.backToLogin')}
            </Link>

            <div>
              <h2 className="text-center text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                {t('forgotPassword.title')}
              </h2>
              <p className="mt-2 text-center text-sm text-gray-400">
                {t('forgotPassword.subtitle')}
              </p>
            </div>

            {success ? (
              <div className="mt-8">
                <div className="flex flex-col items-center justify-center text-center space-y-4">
                  <div className="rounded-full bg-green-500/20 p-3">
                    <CheckCircle className="h-12 w-12 text-green-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">{t('forgotPassword.checkEmail')}</h3>
                  <p className="text-gray-400">
                    {t('forgotPassword.emailSentMessage')} <span className="text-white font-medium">{email}</span>,
                    {t('forgotPassword.emailSentMessage2')}
                  </p>
                  <p className="text-sm text-gray-500">
                    {t('forgotPassword.expireNotice')}
                  </p>
                  <Link
                    to="/login"
                    className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
                  >
                    {t('forgotPassword.returnToLogin')}
                  </Link>
                </div>
              </div>
            ) : (
              <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                <div>
                  <InputField
                    id="email-address"
                    name="email"
                    type="email"
                    placeholder={t('forgotPassword.emailPlaceholder')}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    icon={<Mail className="h-5 w-5 text-gray-400" />}
                    className="appearance-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                  />
                  {email && !validateEmail(email) && (
                    <p className="mt-1 text-xs text-red-400">{t('forgotPassword.invalidEmail')}</p>
                  )}
                </div>

                <ErrorMessage message={error} />

                <div>
                  <LoadingButton
                    type="submit"
                    isLoading={isLoading}
                    disabled={!isFormValid()}
                    loadingText={t('forgotPassword.sendingResetLink')}
                  >
                    {t('forgotPassword.sendResetLink')}
                  </LoadingButton>
                </div>

                <div className="text-center">
                  <span className="text-sm text-gray-400">
                    {t('forgotPassword.rememberPassword')}{' '}
                    <Link to="/login" className="font-medium text-purple-400 hover:text-purple-300">
                      {t('login.signInButton')}
                    </Link>
                  </span>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
