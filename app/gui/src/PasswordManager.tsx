import React, { useState } from 'react';
import { RefreshCw, Key, Shield } from 'lucide-react';
import { filterPasswords, getPasswordStrength } from './utils/passwordUtils';
import { Alert, SearchBar } from './components/ui';
import { PasswordCard, PasswordModal, MasterPasswordModal, FolderSidebar } from './components/password';
import {
  usePasswordManager,
  usePasswordForm,
  useMasterPassword,
  usePasswordVisibility,
  useFolderManager
} from './hooks';
import type { PasswordEntry, PasswordFormData } from './types/password';

const PasswordManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState<PasswordEntry | null>(null);
  const [selectedFolderId, setSelectedFolderId] = useState<string | undefined>(undefined);

  const {
    passwords,
    loading,
    error,
    success,
    generatePassword,
    savePassword,
    deletePassword,
    toggleFavorite,
    decryptPassword,
    copyPasswordToClipboard,
    clearError,
    clearSuccess
  } = usePasswordManager();

  const {
    formData,
    updateFormData,
    resetForm,
    loadEntryIntoForm,
    showPassword: formShowPassword,
    togglePasswordVisibility: toggleFormPasswordVisibility,
    updatePassword
  } = usePasswordForm();

  const {
    masterPassword,
    setMasterPassword,
    showMasterPasswordModal,
    requestMasterPassword,
    submitMasterPassword,
    closeMasterPasswordModal,
    clearPendingAction
  } = useMasterPassword();

  const {
    toggleVisibility,
    showPasswordForEntry,
    setDecryptedPassword,
    getDecryptedPassword,
    isPasswordVisible
  } = usePasswordVisibility();

  const {
    folders,
    error: foldersError,
    createFolder,
    deleteFolder,
    clearError: clearFoldersError,
    fetchFolders
  } = useFolderManager();

  const handleGeneratePassword = async () => {
    const password = await generatePassword();
    if (password) {
      updatePassword(password);
    }
  };

  const handleSubmit = async (formData: PasswordFormData) => {
    // If no master password in form data, check if we need to request it
    if (!formData.master_password) {
      // If we don't have a master password in state, show the modal
      if (!requestMasterPassword({ type: 'submit', data: formData })) {
        return;
      }
      // If we have it in state, use it
      formData = { ...formData, master_password: masterPassword };
    }

    const success = await savePassword(formData, editingEntry?.id || null);
    if (success) {
      setShowModal(false);
      setEditingEntry(null);
      resetForm(masterPassword);
      // Reload folders to update counts
      await fetchFolders();
    }
  };

  const handleDecrypt = async (entryId: string) => {
    if (!requestMasterPassword({ type: 'decrypt', data: entryId })) {
      return;
    }

    const decryptedPwd = await decryptPassword(entryId, masterPassword);
    if (decryptedPwd) {
      setDecryptedPassword(entryId, decryptedPwd);
      showPasswordForEntry(entryId);
    }
  };

  const handleCopyPassword = async (entryId: string) => {
    let password = getDecryptedPassword(entryId);

    if (!password) {
      if (!requestMasterPassword({ type: 'decrypt', data: entryId })) {
        return;
      }
      const decryptedPwd = await decryptPassword(entryId, masterPassword);
      if (decryptedPwd) {
        password = decryptedPwd;
        setDecryptedPassword(entryId, decryptedPwd);
      }
    }

    if (password) {
      await copyPasswordToClipboard(password);
    }
  };

  const handleDelete = async (entryId: string) => {
    if (!requestMasterPassword({ type: 'delete', data: entryId })) {
      return;
    }

    const success = await deletePassword(entryId, masterPassword);
    if (success) {
      // Reload folders to update counts
      await fetchFolders();
    }
  };

  const handleToggleFavorite = async (entry: PasswordEntry) => {
    if (!requestMasterPassword({ type: 'favorite', data: entry })) {
      return;
    }

    await toggleFavorite(entry, masterPassword);
  };

  const handleMasterPasswordSubmit = (password: string) => {
    const action = submitMasterPassword(password);
    updateFormData({ master_password: password });

    if (action && action.data) {
      switch (action.type) {
        case 'submit':
          // Use the formData that was saved in the pending action, not current state
          if (typeof action.data === 'object' && 'name' in action.data) {
            handleSubmit({ ...(action.data as PasswordFormData), master_password: password });
          }
          break;
        case 'decrypt':
          if (typeof action.data === 'string') {
            handleDecrypt(action.data);
          }
          break;
        case 'delete':
          if (typeof action.data === 'string') {
            handleDelete(action.data);
          }
          break;
        case 'favorite':
          if (typeof action.data === 'object' && 'id' in action.data) {
            handleToggleFavorite(action.data as PasswordEntry);
          }
          break;
      }
      clearPendingAction();
    }
  };

  const handleAddPassword = () => {
    setEditingEntry(null);
    resetForm(masterPassword);
    setShowModal(true);
  };

  const handleEditPassword = (entry: PasswordEntry) => {
    setEditingEntry(entry);
    loadEntryIntoForm(entry, masterPassword);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingEntry(null);
    resetForm(masterPassword);
  };

  const handleToggleVisibility = (entryId: string) => {
    if (isPasswordVisible(entryId)) {
      toggleVisibility(entryId);
    } else {
      handleDecrypt(entryId);
    }
  };

  const handleFolderCreate = async (name: string, icon?: string, color?: string) => {
    await createFolder(name, undefined, icon, color);
  };

  const handleFolderDelete = async (folderId: string) => {
    await deleteFolder(folderId);
  };

  const handleFolderSelect = (folderId: string | undefined) => {
    setSelectedFolderId(folderId);
  };

  // Filter passwords by search query and selected folder
  let filteredPasswords = filterPasswords(passwords, searchQuery);
  if (selectedFolderId) {
    filteredPasswords = filteredPasswords.filter(p => p.folder?.id === selectedFolderId);
  }

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900 flex overflow-hidden">
      {/* Folder Sidebar */}
      <FolderSidebar
        folders={folders}
        selectedFolderId={selectedFolderId}
        onSelectFolder={handleFolderSelect}
        onCreateFolder={handleFolderCreate}
        onDeleteFolder={handleFolderDelete}
      />

      {/* Main Content */}
      <div className="flex-1 min-w-0 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Shield className="h-8 w-8 text-indigo-600" />
            Password Manager
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Securely manage all your passwords in one place
          </p>
        </div>

        {/* Alerts */}
        {error && <Alert type="error" message={error} onClose={clearError} />}
        {success && <Alert type="success" message={success} onClose={clearSuccess} />}
        {foldersError && <Alert type="error" message={foldersError} onClose={clearFoldersError} />}

        {/* Search and Actions Bar */}
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          onAddPassword={handleAddPassword}
        />

        {/* Password Cards Grid */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
          </div>
        ) : filteredPasswords.length === 0 ? (
          <div className="text-center py-12">
            <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No passwords found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {searchQuery ? 'Try a different search term' : 'Get started by adding your first password'}
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredPasswords.map((entry) => (
              <PasswordCard
                key={entry.id}
                entry={entry}
                showPassword={isPasswordVisible(entry.id)}
                decryptedPassword={getDecryptedPassword(entry.id)}
                onToggleFavorite={handleToggleFavorite}
                onCopyPassword={handleCopyPassword}
                onToggleVisibility={handleToggleVisibility}
                onEdit={handleEditPassword}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Add/Edit Modal */}
        <PasswordModal
          isOpen={showModal}
          onClose={handleCloseModal}
          editingEntry={editingEntry}
          onSubmit={handleSubmit}
          onGeneratePassword={handleGeneratePassword}
          formData={formData}
          onFormDataChange={updateFormData}
          showPassword={formShowPassword['form'] || false}
          onTogglePasswordVisibility={() => toggleFormPasswordVisibility('form')}
          passwordStrength={passwordStrength}
          folders={folders}
        />

        {/* Master Password Modal */}
        <MasterPasswordModal
          isOpen={showMasterPasswordModal}
          onClose={closeMasterPasswordModal}
          onSubmit={handleMasterPasswordSubmit}
          masterPassword={masterPassword}
          onMasterPasswordChange={setMasterPassword}
        />
        </div>
      </div>
    </div>
  );
};

export default PasswordManager;
