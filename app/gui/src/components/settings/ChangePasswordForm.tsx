import React, { useState } from 'react';
import { Lock, CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useChangePassword } from '../../hooks/useChangePassword';
import { usePasswordStrength } from '../../hooks/usePasswordStrength';
import { InputField, ErrorMessage, LoadingButton, PasswordStrengthIndicator } from '../ui';

const ChangePasswordForm: React.FC = () => {
  const { t } = useTranslation();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { isLoading, error, success, changePassword } = useChangePassword();
  const passwordStrength = usePasswordStrength(newPassword);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const result = await changePassword(currentPassword, newPassword, confirmPassword);
    
    if (result) {
      // Clear form on success
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    }
  };

  const isFormValid = () => {
    return currentPassword.length > 0 && 
           newPassword.length >= 8 && 
           confirmPassword.length >= 8 && 
           newPassword === confirmPassword;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Lock className="h-5 w-5 text-indigo-600" />
          {t('changePassword.title')}
        </h3>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {t('changePassword.subtitle')}
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {t('changePassword.successTitle')}
            </p>
            <p className="text-xs text-green-700 dark:text-green-300 mt-1">
              {t('changePassword.successMessage')}
            </p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="current-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('changePassword.currentPassword')}
          </label>
          <InputField
            id="current-password"
            name="currentPassword"
            type="password"
            placeholder={t('changePassword.currentPasswordPlaceholder')}
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
            autoComplete="current-password"
            icon={<Lock className="h-5 w-5 text-gray-400" />}
            showToggle
            showPassword={showCurrentPassword}
            onTogglePassword={() => setShowCurrentPassword(!showCurrentPassword)}
            className="appearance-none relative block w-full px-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300"
          />
        </div>

        <div>
          <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('changePassword.newPassword')}
          </label>
          <InputField
            id="new-password"
            name="newPassword"
            type="password"
            placeholder={t('changePassword.newPasswordPlaceholder')}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            autoComplete="new-password"
            icon={<Lock className="h-5 w-5 text-gray-400" />}
            showToggle
            showPassword={showNewPassword}
            onTogglePassword={() => setShowNewPassword(!showNewPassword)}
            className="appearance-none relative block w-full px-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300"
          />
          <PasswordStrengthIndicator strength={passwordStrength} password={newPassword} />
        </div>

        <div>
          <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('changePassword.confirmPassword')}
          </label>
          <InputField
            id="confirm-password"
            name="confirmPassword"
            type="password"
            placeholder={t('changePassword.confirmPasswordPlaceholder')}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            icon={<Lock className="h-5 w-5 text-gray-400" />}
            showToggle
            showPassword={showConfirmPassword}
            onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
            className="appearance-none relative block w-full px-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300"
          />
          {confirmPassword && newPassword !== confirmPassword && (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{t('register.passwordMismatch')}</p>
          )}
        </div>

        <ErrorMessage message={error} />

        <div className="pt-2">
          <LoadingButton
            type="submit"
            isLoading={isLoading}
            disabled={!isFormValid() || success}
            loadingText={t('changePassword.changing')}
            className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            {t('changePassword.changePassword')}
          </LoadingButton>
        </div>
      </form>
    </div>
  );
};

export default ChangePasswordForm;
