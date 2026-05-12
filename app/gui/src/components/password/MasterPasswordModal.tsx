import React from 'react';
import { Key } from 'lucide-react';
import type { MasterPasswordModalProps } from '../../types/password';

const MasterPasswordModal: React.FC<MasterPasswordModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  masterPassword,
  onMasterPasswordChange
}) => {
  if (!isOpen) return null;

  const handleSubmit = () => {
    if (masterPassword) {
      onSubmit(masterPassword);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && masterPassword) {
      handleSubmit();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
        <div className="flex items-center gap-3 mb-4">
          <Key className="h-6 w-6 text-indigo-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Enter Master Password
          </h2>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Your master password is required to encrypt and decrypt passwords.
        </p>

        <input
          type="password"
          value={masterPassword}
          onChange={(e) => onMasterPasswordChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter your master password"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
          autoFocus
        />

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!masterPassword}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default MasterPasswordModal;