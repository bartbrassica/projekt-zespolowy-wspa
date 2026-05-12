import React from 'react';
import { Mail, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLoginForm } from './hooks/useLoginForm';
import { useLogin } from './hooks/useLogin';
import { InputField, ErrorMessage, LoadingButton, Checkbox } from './components/ui';
import type { LoginProps } from './types/auth';

const Login: React.FC<LoginProps> = ({ onSuccess }) => {
  const {
    formData,
    showPassword,
    setShowPassword,
    handleEmailChange,
    handlePasswordChange,
    handleRememberMeChange,
    isFormValid
  } = useLoginForm();

  const { handleLogin, isLoading, error } = useLogin(onSuccess);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleLogin(formData);
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated Background with Mouse Tracking (matching landing page) */}
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
            <div>
              <h2 className="mt-6 text-center text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Sign in to your account
              </h2>
              <p className="mt-2 text-center text-sm text-gray-400">
            </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              <div className="rounded-md shadow-sm -space-y-px">
                <InputField
                  id="email-address"
                  name="email"
                  type="email"
                  placeholder="Email address"
                  value={formData.email}
                  onChange={handleEmailChange}
                  required
                  autoComplete="email"
                  icon={<Mail className="h-5 w-5 text-gray-400" />}
                  className="appearance-none rounded-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-t-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                />

                <InputField
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handlePasswordChange}
                  required
                  autoComplete="current-password"
                  icon={<Lock className="h-5 w-5 text-gray-400" />}
                  showToggle
                  showPassword={showPassword}
                  onTogglePassword={() => setShowPassword(!showPassword)}
                  className="appearance-none rounded-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-b-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                />
              </div>

              <ErrorMessage message={error} />

              <div className="flex items-center justify-between">
                <Checkbox
                  id="remember-me"
                  name="remember-me"
                  checked={formData.rememberMe}
                  onChange={handleRememberMeChange}
                  label="Remember me"
                />

                <div className="text-sm">
                  <Link to="/forgot-password" className="font-medium text-purple-400 hover:text-purple-300">
                    Forgot your password?
                  </Link>
                </div>
              </div>

              <div>
                <LoadingButton
                  type="submit"
                  isLoading={isLoading}
                  disabled={!isFormValid()}
                  loadingText="Signing in..."
                >
                  Sign in
                </LoadingButton>
              </div>

              <div className="text-center">
                <span className="text-sm text-gray-400">
                  Don't have an account?{' '}
                  <Link to="/signup" className="font-medium text-purple-400 hover:text-purple-300">
                    Sign up
                  </Link>
                </span>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;