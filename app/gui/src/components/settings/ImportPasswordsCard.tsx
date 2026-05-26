import React, { useState, useRef } from 'react';
import { Upload, Lock, CheckCircle, AlertCircle, FileSpreadsheet } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { authApi } from '../../services/authApi';
import { InputField, ErrorMessage, LoadingButton } from '../ui';

const ImportPasswordsCard: React.FC = () => {
  const { t } = useTranslation();
  const [masterPassword, setMasterPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validExtensions = ['.xlsx', '.csv', '.json'];
      const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));

      if (!validExtensions.includes(fileExtension)) {
        setError(t('importPasswords.invalidFileType'));
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      setError('');
      setSuccess('');
    }
  };

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      setError(t('importPasswords.noFileSelected'));
      return;
    }

    if (!masterPassword) {
      setError(t('importPasswords.noMasterPassword'));
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      // Read file as base64
      const reader = new FileReader();

      reader.onload = async (event) => {
        try {
          const base64Data = event.target?.result as string;
          // Remove data URL prefix if present
          const base64Content = base64Data.includes(',')
            ? base64Data.split(',')[1]
            : base64Data;

          // Determine format from file extension
          const fileExtension = selectedFile.name.toLowerCase().slice(selectedFile.name.lastIndexOf('.'));
          let format: 'csv' | 'json' | 'xlsx' = 'xlsx';

          if (fileExtension === '.csv') format = 'csv';
          else if (fileExtension === '.json') format = 'json';
          else if (fileExtension === '.xlsx') format = 'xlsx';

          const result = await authApi.importPasswords(masterPassword, base64Content, format);

          setSuccess(result.message);
          setMasterPassword('');
          setSelectedFile(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }

          // Clear success message after 5 seconds
          setTimeout(() => setSuccess(''), 5000);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to import passwords');
        } finally {
          setIsLoading(false);
        }
      };

      reader.onerror = () => {
        setError('Failed to read file');
        setIsLoading(false);
      };

      reader.readAsDataURL(selectedFile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import passwords');
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-indigo-600" />
          {t('importPasswords.title')}
        </h3>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {t('importPasswords.subtitle')}
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {success}
            </p>
          </div>
        </div>
      )}

      <form onSubmit={handleImport} className="space-y-5">
        <div>
          <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('importPasswords.selectFile')}
          </label>
          <div className="mt-1 flex items-center gap-3">
            <input
              ref={fileInputRef}
              id="file-upload"
              type="file"
              accept=".xlsx,.csv,.json"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-300 flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              {t('importPasswords.selectFile')}
            </button>
            {selectedFile && (
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {selectedFile.name}
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {t('importPasswords.fileFormatText')}
          </p>
        </div>

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
            disabled={!selectedFile || !masterPassword || isLoading}
            loadingText={t('importPasswords.importing')}
            className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            {t('importPasswords.importButton')}
          </LoadingButton>
        </div>
      </form>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
              {t('importPasswords.importGuidelinesTitle')}
            </h4>
            <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
              <li>• {t('importPasswords.guideline1')}</li>
              <li>• {t('importPasswords.guideline2')}</li>
              <li>• {t('importPasswords.guideline3')}</li>
              <li>• {t('importPasswords.guideline4')}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportPasswordsCard;
