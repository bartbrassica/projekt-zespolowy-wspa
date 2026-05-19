import React, { useState } from 'react';
import { Share2, X, Copy, CheckCircle2 } from 'lucide-react';
import type { ShareModalProps, ShareLinkFormData } from '../../types/password';
import { useShareLinks } from '../../hooks';

const ShareModal: React.FC<ShareModalProps> = ({
  isOpen,
  onClose,
  passwordEntry,
  onCreateShareLink
}) => {
  const [masterPassword, setMasterPassword] = useState('');
  const [maxViews, setMaxViews] = useState(1);
  const [expiresInHours, setExpiresInHours] = useState(24);
  const [requireAuthentication, setRequireAuthentication] = useState(false);
  const [allowedEmail, setAllowedEmail] = useState('');
  const [copiedUrl, setCopiedUrl] = useState(false);

  const { loading, error, createdLink, createShareLink, clearError, clearCreatedLink } = useShareLinks();

  if (!isOpen) return null;

  const handleSubmit = async () => {
    clearError();

    const formData: ShareLinkFormData = {
      password_entry_id: passwordEntry.id,
      master_password: masterPassword,
      max_views: maxViews,
      expires_in_hours: expiresInHours,
      require_authentication: requireAuthentication,
      allowed_email: allowedEmail || undefined
    };

    const result = await createShareLink(formData);
    if (result) {
      onCreateShareLink(formData);
      // Reset form for next use but keep modal open to show share link
      setMasterPassword('');
    }
  };

  const handleClose = () => {
    setMasterPassword('');
    setMaxViews(1);
    setExpiresInHours(24);
    setRequireAuthentication(false);
    setAllowedEmail('');
    clearCreatedLink();
    clearError();
    setCopiedUrl(false);
    onClose();
  };

  const handleCopyUrl = async () => {
    if (createdLink?.share_url) {
      await navigator.clipboard.writeText(createdLink.share_url);
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2000);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && masterPassword && !createdLink) {
      handleSubmit();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Share2 className="h-6 w-6 text-indigo-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Share Password
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Create a secure share link for: <strong>{passwordEntry.name}</strong>
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {!createdLink ? (
          <>
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Master Password *
                </label>
                <input
                  type="password"
                  value={masterPassword}
                  onChange={(e) => setMasterPassword(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter your master password"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Maximum Views
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={maxViews}
                  onChange={(e) => setMaxViews(Math.max(1, Math.min(100, parseInt(e.target.value) || 1)))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  How many times the link can be accessed (1-100)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Expires In (hours)
                </label>
                <input
                  type="number"
                  min="1"
                  max="168"
                  value={expiresInHours}
                  onChange={(e) => setExpiresInHours(Math.max(1, Math.min(168, parseInt(e.target.value) || 24)))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Link will expire in this many hours (max 168 = 1 week)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Allowed Email (optional)
                </label>
                <input
                  type="email"
                  value={allowedEmail}
                  onChange={(e) => setAllowedEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Restrict access to specific email address
                </p>
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={requireAuthentication}
                    onChange={(e) => setRequireAuthentication(e.target.checked)}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Require authentication
                  </span>
                </label>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleClose}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!masterPassword || loading}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Share Link'}
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                <h3 className="font-medium text-green-800 dark:text-green-300">
                  Share Link Created!
                </h3>
              </div>

              <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Max Views:</span>
                  <span>{createdLink.max_views}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Current Views:</span>
                  <span>{createdLink.current_views}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Expires:</span>
                  <span>{new Date(createdLink.expires_at).toLocaleString()}</span>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Share URL
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={createdLink.share_url}
                    readOnly
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={handleCopyUrl}
                    className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  >
                    {copiedUrl ? (
                      <>
                        <CheckCircle2 className="h-4 w-4" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        Copy
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            <button
              onClick={handleClose}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Done
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ShareModal;
