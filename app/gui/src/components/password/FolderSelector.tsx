import React from 'react';
import { Folder as FolderIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Folder } from '../../types/password';

interface FolderSelectorProps {
  folders: Folder[];
  selectedFolderId?: string;
  onChange: (folderId: string | undefined) => void;
  label?: string;
}

export const FolderSelector: React.FC<FolderSelectorProps> = ({
  folders,
  selectedFolderId,
  onChange,
  label
}) => {
  const { t } = useTranslation();

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        <FolderIcon className="inline h-4 w-4 mr-1" />
        {label || t('folders.folder')}
      </label>
      <select
        value={selectedFolderId || ''}
        onChange={(e) => onChange(e.target.value || undefined)}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      >
        <option value="">{t('folders.noFolder')}</option>
        {folders.map((folder) => (
          <option key={folder.id} value={folder.id}>
            {folder.icon && `${folder.icon} `}
            {folder.name}
            {folder.entry_count > 0 && ` (${folder.entry_count})`}
          </option>
        ))}
      </select>
    </div>
  );
};

export default FolderSelector;
