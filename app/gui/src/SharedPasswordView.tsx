import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router';
import { useTranslation } from 'react-i18next';
import { Shield, ExternalLink, Copy, Eye, EyeOff, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { authApi } from './services/authApi';
import type { SharedPasswordData } from './types/password';
import { decryptPassword } from './utils/encryption';

const SharedPasswordView: React.FC = () => {
  const { t } = useTranslation();
  const { shareToken } = useParams<{ shareToken: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [passwordData, setPasswordData] = useState<SharedPasswordData | null>(null);
  const [decryptedPassword, setDecryptedPassword] = useState<string>('');
  const [decrypting, setDecrypting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [copiedUsername, setCopiedUsername] = useState(false);
  const [copiedPassword, setCopiedPassword] = useState(false);

  useEffect(() => {
    if (shareToken) {
      fetchSharedPassword(shareToken);
    } else {
      setError(t('sharedPasswordView.invalidShareLink'));
      setLoading(false);
    }
  }, [shareToken, location.hash, t]);

  const fetchSharedPassword = async (token: string) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch encrypted password data
      const data = await authApi.getSharedPassword(token);
      setPasswordData(data);

      // Extract encryption key from URL fragment (after #)
      const hash = location.hash.slice(1); // Remove the # character
      if (!hash) {
        setError(t('sharedPasswordView.missingEncryptionKey'));
        setLoading(false);
        return;
      }

      // Decode the encryption key from base64url
      const encryptionKey = atob(hash.replace(/-/g, '+').replace(/_/g, '/'));

      // Decrypt the password
      setDecrypting(true);
      const decrypted = await decryptPassword(
        data.encrypted_password,
        encryptionKey,
        data.encryption_salt
      );

      if (decrypted === null) {
        setError(t('sharedPasswordView.failedToDecrypt'));
        setLoading(false);
        return;
      }

      setDecryptedPassword(decrypted);
    } catch (err: any) {
      setError(err.message || t('sharedPasswordView.failedToAccess'));
    } finally {
      setLoading(false);
      setDecrypting(false);
    }
  };

  const handleCopy = async (text: string, type: 'username' | 'password') => {
    await navigator.clipboard.writeText(text);
    if (type === 'username') {
      setCopiedUsername(true);
      setTimeout(() => setCopiedUsername(false), 2000);
    } else {
      setCopiedPassword(true);
      setTimeout(() => setCopiedPassword(false), 2000);
    }
  };

  const getSiteHostname = (url: string) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch {
      return url;
    }
  };

  if (loading || decrypting) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            {decrypting ? t('sharedPasswordView.decryptingPassword') : t('sharedPasswordView.loadingSharedPassword')}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('sharedPasswordView.unableToAccess')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error}
          </p>
          <div className="space-y-2 text-sm text-gray-500 dark:text-gray-400 text-left bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <p className="font-medium">{t('sharedPasswordView.possibleReasons')}</p>
            <ul className="list-disc list-inside space-y-1">
              <li>{t('sharedPasswordView.linkExpired')}</li>
              <li>{t('sharedPasswordView.maxViewsReached')}</li>
              <li>{t('sharedPasswordView.linkInvalid')}</li>
            </ul>
          </div>
          <button
            onClick={() => navigate('/')}
            className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {t('sharedPasswordView.goToHome')}
          </button>
        </div>
      </div>
    );
  }

  if (!passwordData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="h-10 w-10 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('sharedPasswordView.sharedPassword')}
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            {t('sharedPasswordView.someoneShared')}
          </p>
        </div>

        {/* Password Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-6">
          <div className="space-y-6">
            {/* Name */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                {passwordData.name}
              </h2>
              {passwordData.site && (
                <a
                  href={passwordData.site}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700"
                >
                  <ExternalLink className="h-4 w-4" />
                  {getSiteHostname(passwordData.site)}
                </a>
              )}
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('sharedPasswordView.username')}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={passwordData.username}
                  readOnly
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                />
                <button
                  onClick={() => handleCopy(passwordData.username, 'username')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  {copiedUsername ? (
                    <>
                      <CheckCircle2 className="h-4 w-4" />
                      {t('sharedPasswordView.copied')}
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      {t('sharedPasswordView.copy')}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('sharedPasswordView.password')}
              </label>
              <div className="flex gap-2">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={decryptedPassword}
                  readOnly
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
                <button
                  onClick={() => handleCopy(decryptedPassword, 'password')}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  disabled={!decryptedPassword}
                >
                  {copiedPassword ? (
                    <>
                      <CheckCircle2 className="h-4 w-4" />
                      {t('sharedPasswordView.copied')}
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      {t('sharedPasswordView.copy')}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
            <div className="text-sm text-yellow-800 dark:text-yellow-300">
              <p className="font-medium mb-1">{t('sharedPasswordView.securityNotice')}</p>
              <p>
                {t('sharedPasswordView.securityNoticeText')}
              </p>
              <div className="mt-3 space-y-1">
                <p>
                  <span className="font-medium">{t('sharedPasswordView.remainingViews')}</span> {passwordData.views_remaining}
                </p>
                <p>
                  <span className="font-medium">{t('sharedPasswordView.expiresAt')}</span>{' '}
                  {new Date(passwordData.expires_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
          >
            {t('sharedPasswordView.returnToHome')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SharedPasswordView;
