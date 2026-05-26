import React from 'react';
import { Settings } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import ChangePasswordForm from '../settings/ChangePasswordForm';
import ExportPasswordsCard from '../settings/ExportPasswordsCard';
import ImportPasswordsCard from '../settings/ImportPasswordsCard';
import { LanguageSwitcher } from '../ui';

const SettingsPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <Settings className="h-8 w-8 text-indigo-600" />
                {t('settings.settings')}
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                {t('settings.subtitle')}
              </p>
            </div>
            <LanguageSwitcher />
          </div>
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Account Security Section */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('settings.accountSecurity')}
            </h2>
            <ChangePasswordForm />
          </div>

          {/* Data Management Section */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('settings.dataManagement')}
            </h2>
            <div className="space-y-6">
              <ImportPasswordsCard />
              <ExportPasswordsCard />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;