import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import { useForgotPassword } from './hooks/useForgotPassword';
import { validateEmail } from './utils/passwordResetUtils';
import { InputField, ErrorMessage, LoadingButton } from './components/ui';

const ForgotPassword: React.FC = () => {
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
            DigitaLockbox
          </Link>
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
              Back to Login
            </Link>

            <div>
              <h2 className="text-center text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Forgot Password?
              </h2>
              <p className="mt-2 text-center text-sm text-gray-400">
                Enter your email address and we'll send you a link to reset your password
              </p>
            </div>

            {success ? (
              <div className="mt-8">
                <div className="flex flex-col items-center justify-center text-center space-y-4">
                  <div className="rounded-full bg-green-500/20 p-3">
                    <CheckCircle className="h-12 w-12 text-green-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">Check your email</h3>
                  <p className="text-gray-400">
                    If an account exists for <span className="text-white font-medium">{email}</span>, 
                    you will receive a password reset link shortly.
                  </p>
                  <p className="text-sm text-gray-500">
                    The link will expire in 24 hours. If you don't see the email, check your spam folder.
                  </p>
                  <Link 
                    to="/login"
                    className="mt-4 text-purple-400 hover:text-purple-300 font-medium"
                  >
                    Return to login
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
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    icon={<Mail className="h-5 w-5 text-gray-400" />}
                    className="appearance-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                  />
                  {email && !validateEmail(email) && (
                    <p className="mt-1 text-xs text-red-400">Please enter a valid email address</p>
                  )}
                </div>

                <ErrorMessage message={error} />

                <div>
                  <LoadingButton
                    type="submit"
                    isLoading={isLoading}
                    disabled={!isFormValid()}
                    loadingText="Sending reset link..."
                  >
                    Send Reset Link
                  </LoadingButton>
                </div>

                <div className="text-center">
                  <span className="text-sm text-gray-400">
                    Remember your password?{' '}
                    <Link to="/login" className="font-medium text-purple-400 hover:text-purple-300">
                      Sign in
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
