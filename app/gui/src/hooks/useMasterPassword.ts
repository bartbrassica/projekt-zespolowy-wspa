import { useState } from 'react';
import type { PendingAction } from '../types/password';

export const useMasterPassword = () => {
  const [masterPassword, setMasterPassword] = useState('');
  const [showMasterPasswordModal, setShowMasterPasswordModal] = useState(false);
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);

  const requestMasterPassword = (action: PendingAction) => {
    if (!masterPassword) {
      setShowMasterPasswordModal(true);
      setPendingAction(action);
      return false;
    }
    return true;
  };

  const submitMasterPassword = (password: string) => {
    setMasterPassword(password);
    setShowMasterPasswordModal(false);
    return pendingAction;
  };

  const closeMasterPasswordModal = () => {
    setShowMasterPasswordModal(false);
    setPendingAction(null);
  };

  const clearPendingAction = () => {
    setPendingAction(null);
  };

  return {
    masterPassword,
    setMasterPassword,
    showMasterPasswordModal,
    pendingAction,
    requestMasterPassword,
    submitMasterPassword,
    closeMasterPasswordModal,
    clearPendingAction
  };
};