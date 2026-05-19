import { useState } from 'react';

interface ConfirmDialogState {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  type?: 'danger' | 'warning' | 'info';
  confirmText?: string;
  cancelText?: string;
}

const initialState: ConfirmDialogState = {
  isOpen: false,
  title: '',
  message: '',
  onConfirm: () => {},
  type: 'danger',
  confirmText: 'Confirm',
  cancelText: 'Cancel'
};

export const useConfirmDialog = () => {
  const [dialogState, setDialogState] = useState<ConfirmDialogState>(initialState);

  const showConfirm = (
    title: string,
    message: string,
    onConfirm: () => void,
    options?: {
      type?: 'danger' | 'warning' | 'info';
      confirmText?: string;
      cancelText?: string;
    }
  ) => {
    setDialogState({
      isOpen: true,
      title,
      message,
      onConfirm,
      type: options?.type || 'danger',
      confirmText: options?.confirmText || 'Confirm',
      cancelText: options?.cancelText || 'Cancel'
    });
  };

  const closeDialog = () => {
    setDialogState(initialState);
  };

  const handleConfirm = () => {
    dialogState.onConfirm();
    closeDialog();
  };

  return {
    dialogState,
    showConfirm,
    closeDialog,
    handleConfirm
  };
};
