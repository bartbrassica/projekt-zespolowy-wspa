import React from 'react';
import { Mail, Lock, User, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useRegisterForm } from './hooks/useRegisterForm';
import { usePasswordStrength } from './hooks/usePasswordStrength';
import { useRegistration } from './hooks/useRegistration';
import { validatePasswordMatch } from './utils/passwordValidation';
import InputField from './components/ui/InputField';
import PasswordStrengthIndicator from './components/ui/PasswordStrengthIndicator';
import ErrorMessage from './components/ui/ErrorMessage';
import LoadingButton from './components/ui/LoadingButton';

const Register: React.FC = () => {
  const {
    formData,
    showPassword,
    setShowPassword,
    showConfirmPassword,
    setShowConfirmPassword,
    handleChange,
    validateForm,
    isFormValid
  } = useRegisterForm();

  const { register, isLoading, error } = useRegistration();
  const passwordStrength = usePasswordStrength(formData.password);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      return;
    }

    await register(formData);
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated Background (matching landing page) */}
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
        <div className="w-full max-w-md">
          <div className="bg-gray-900 bg-opacity-50 backdrop-blur-xl rounded-2xl p-8 border border-gray-800 shadow-2xl">
            <div>
              <h2 className="mt-6 text-center text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Create your account
              </h2>
              <p className="mt-2 text-center text-sm text-gray-400">
                Join DigitaLockbox and secure your digital life
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <InputField
                  id="first_name"
                  name="first_name"
                  type="text"
                  placeholder="First name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  icon={<User className="h-5 w-5 text-gray-400" />}
                />

                <InputField
                  id="last_name"
                  name="last_name"
                  type="text"
                  placeholder="Last name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  icon={<User className="h-5 w-5 text-gray-400" />}
                />
              </div>

              {/* Email Field */}
              <InputField
                id="email"
                name="email"
                type="email"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
                required
                autoComplete="email"
                icon={<Mail className="h-5 w-5 text-gray-400" />}
              />

              {/* Phone Field */}
              <InputField
                id="phone_number"
                name="phone_number"
                type="tel"
                placeholder="Phone number"
                value={formData.phone_number}
                onChange={handleChange}
                required
                icon={<Phone className="h-5 w-5 text-gray-400" />}
              />

              {/* Password Field */}
              <div>
                <InputField
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  icon={<Lock className="h-5 w-5 text-gray-400" />}
                  showToggle
                  showPassword={showPassword}
                  onTogglePassword={() => setShowPassword(!showPassword)}
                />
                <PasswordStrengthIndicator strength={passwordStrength} password={formData.password} />
              </div>

              {/* Confirm Password Field */}
              <div>
                <InputField
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="Confirm password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  icon={<Lock className="h-5 w-5 text-gray-400" />}
                  showToggle
                  showPassword={showConfirmPassword}
                  onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
                />
                {formData.confirmPassword && !validatePasswordMatch(formData.password, formData.confirmPassword) && (
                  <p className="text-xs mt-1 text-red-400">Passwords do not match</p>
                )}
              </div>

              <ErrorMessage message={error} />

              <div>
                <LoadingButton
                  type="submit"
                  isLoading={isLoading}
                  disabled={!isFormValid()}
                  loadingText="Creating account..."
                >
                  Create account
                </LoadingButton>
              </div>

              <div className="text-center">
                <span className="text-sm text-gray-400">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-purple-400 hover:text-purple-300">
                    Sign in
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

export default Register;