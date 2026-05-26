import React, { useState } from 'react';
import { Download, Lock, CheckCircle, AlertCircle, FileSpreadsheet } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { authApi } from '../../services/authApi';
import { InputField, ErrorMessage, LoadingButton } from '../ui';

const ExportPasswordsCard: React.FC = () => {
  const { t } = useTranslation();
  const [masterPassword, setMasterPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!masterPassword) {
      setError(t('exportPasswords.noMasterPassword'));
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      const result = await authApi.exportPasswords(masterPassword, 'xlsx', true);

      // Convert base64 to blob and download
      const byteCharacters = atob(result.data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(true);
      setMasterPassword('');

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('exportPasswords.exportFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-indigo-600" />
          {t('exportPasswords.title')}
        </h3>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {t('exportPasswords.subtitle')}
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {t('exportPasswords.successTitle')}
            </p>
            <p className="text-xs text-green-700 dark:text-green-300 mt-1">
              {t('exportPasswords.successMessage')}
            </p>
          </div>
        </div>
      )}

      <form onSubmit={handleExport} className="space-y-5">
        <div>
          <label htmlFor="master-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('common.masterPassword')}
          </label>
          <InputField
            id="master-password"
            name="masterPassword"
            type="password"
            placeholder={t('common.masterPasswordPlaceholder')}
            value={masterPassword}
            onChange={(e) => setMasterPassword(e.target.value)}
            required
            autoComplete="current-password"
            icon={<Lock className="h-5 w-5 text-gray-400" />}
            showToggle
            showPassword={showPassword}
            onTogglePassword={() => setShowPassword(!showPassword)}
            className="appearance-none relative block w-full px-10 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300"
          />
        </div>

        <ErrorMessage message={error} />

        <div className="pt-2">
          <LoadingButton
            type="submit"
            isLoading={isLoading}
            disabled={!masterPassword || success}
            loadingText={t('exportPasswords.exporting')}
            className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            {t('exportPasswords.exportButton')}
          </LoadingButton>
        </div>
      </form>

      <div className="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-2">
              {t('exportPasswords.securityNoticeTitle')}
            </h4>
            <ul className="text-xs text-amber-800 dark:text-amber-300 space-y-1">
              <li>• {t('exportPasswords.securityNotice1')}</li>
              <li>• {t('exportPasswords.securityNotice2')}</li>
              <li>• {t('exportPasswords.securityNotice3')}</li>
              <li>• {t('exportPasswords.securityNotice4')}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportPasswordsCard;
