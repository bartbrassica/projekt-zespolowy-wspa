import React, { useState } from 'react';
import { Folder as FolderIcon, Plus, Trash2, X, Tag as TagIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Folder, Tag } from '../../types/password';

interface FolderSidebarProps {
  folders: Folder[];
  selectedFolderId?: string;
  onSelectFolder: (folderId: string | undefined) => void;
  onCreateFolder: (name: string, icon?: string, color?: string) => void;
  onDeleteFolder: (folderId: string) => void;
  tags?: Tag[];
  selectedTagIds?: string[];
  onSelectTag?: (tagId: string) => void;
  onCreateTag?: (name: string, color?: string) => void;
  onDeleteTag?: (tagId: string) => void;
}

export const FolderSidebar: React.FC<FolderSidebarProps> = ({
  folders,
  selectedFolderId,
  onSelectFolder,
  onCreateFolder,
  onDeleteFolder,
  tags = [],
  selectedTagIds = [],
  onSelectTag,
  onCreateTag,
  onDeleteTag
}) => {
  const { t } = useTranslation();
  const [isCreating, setIsCreating] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderIcon, setNewFolderIcon] = useState('📁');
  const [isCreatingTag, setIsCreatingTag] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#6366f1');

  const handleCreate = () => {
    if (newFolderName.trim()) {
      onCreateFolder(newFolderName.trim(), newFolderIcon);
      setNewFolderName('');
      setNewFolderIcon('📁');
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    setNewFolderName('');
    setNewFolderIcon('📁');
    setIsCreating(false);
  };

  const handleCreateTag = () => {
    if (newTagName.trim() && onCreateTag) {
      onCreateTag(newTagName.trim(), newTagColor);
      setNewTagName('');
      setNewTagColor('#6366f1');
      setIsCreatingTag(false);
    }
  };

  const handleCancelTag = () => {
    setNewTagName('');
    setNewTagColor('#6366f1');
    setIsCreatingTag(false);
  };

  return (
    <div className="w-[28rem] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 overflow-y-auto flex-shrink-0">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <FolderIcon className="h-6 w-6" />
          {t('folders.folders')}
        </h2>
        <button
          onClick={() => setIsCreating(true)}
          className="p-1 text-indigo-600 hover:bg-indigo-50 dark:hover:bg-gray-700 rounded transition-colors"
          title={t('folders.newFolder')}
        >
          <Plus className="h-5 w-5" />
        </button>
      </div>

      {/* All Passwords */}
      <button
        onClick={() => onSelectFolder(undefined)}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors mb-3 ${
          selectedFolderId === undefined
            ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
        }`}
      >
        <FolderIcon className="h-5 w-5" />
        <span className="font-medium">{t('folders.allPasswords')}</span>
      </button>

      {/* New Folder Form */}
      {isCreating && (
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-3 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder={t('folders.icon')}
              value={newFolderIcon}
              onChange={(e) => setNewFolderIcon(e.target.value)}
              className="w-14 px-2 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              maxLength={2}
            />
            <input
              type="text"
              placeholder={t('folders.folderName')}
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreate();
                if (e.key === 'Escape') handleCancel();
              }}
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              className="flex-1 px-3 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors font-medium"
            >
              {t('folders.create')}
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      {/* Folder List */}
      <div className="space-y-2">
        {folders.map((folder) => (
          <div
            key={folder.id}
            className={`group flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
              selectedFolderId === folder.id
                ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <button
              onClick={() => onSelectFolder(folder.id)}
              className="flex-1 flex items-center gap-3 text-left"
            >
              <span className="text-xl">{folder.icon || '📁'}</span>
              <span className="flex-1 font-medium truncate">{folder.name}</span>
              <span className="text-sm opacity-60">({folder.entry_count})</span>
            </button>
            <button
              onClick={() => onDeleteFolder(folder.id)}
              className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-all"
              title={t('folders.deleteFolder')}
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
        ))}
      </div>

      {folders.length === 0 && !isCreating && (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-4">
          {t('folders.noFoldersYet')}
        </p>
      )}

      {/* Tags Section */}
      {onCreateTag && (
        <>
          <div className="border-t border-gray-200 dark:border-gray-700 my-6"></div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <TagIcon className="h-6 w-6" />
              {t('tags.tags')}
            </h2>
            <button
              onClick={() => setIsCreatingTag(true)}
              className="p-1 text-indigo-600 hover:bg-indigo-50 dark:hover:bg-gray-700 rounded transition-colors"
              title={t('tags.newTag')}
            >
              <Plus className="h-5 w-5" />
            </button>
          </div>

          {/* New Tag Form */}
          {isCreatingTag && (
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-3 space-y-3">
              <div className="flex gap-2">
                <input
                  type="color"
                  value={newTagColor}
                  onChange={(e) => setNewTagColor(e.target.value)}
                  className="w-14 h-10 border border-gray-300 dark:border-gray-600 rounded cursor-pointer"
                  title={t('tags.tagColor')}
                />
                <input
                  type="text"
                  placeholder={t('tags.tagName')}
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleCreateTag();
                    if (e.key === 'Escape') handleCancelTag();
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  autoFocus
                  maxLength={50}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleCreateTag}
                  className="flex-1 px-3 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors font-medium"
                >
                  {t('tags.create')}
                </button>
                <button
                  onClick={handleCancelTag}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}

          {/* Tag List */}
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => {
              const isSelected = selectedTagIds.includes(tag.id);
              return (
                <div
                  key={tag.id}
                  className="group relative"
                >
                  <button
                    onClick={() => onSelectTag && onSelectTag(tag.id)}
                    className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      isSelected
                        ? 'ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-gray-800'
                        : 'opacity-70 hover:opacity-100'
                    }`}
                    style={{
                      backgroundColor: tag.color ? `${tag.color}30` : '#e5e7eb',
                      color: tag.color || '#6b7280',
                      borderLeft: `3px solid ${tag.color || '#9ca3af'}`
                    }}
                  >
                    <span>{tag.name}</span>
                    <span className="ml-2 text-xs opacity-60">({tag.entry_count})</span>
                  </button>
                  {onDeleteTag && (
                    <button
                      onClick={() => onDeleteTag(tag.id)}
                      className="absolute -top-1 -right-1 opacity-0 group-hover:opacity-100 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all shadow-sm"
                      title={t('tags.deleteTag')}
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          {tags.length === 0 && !isCreatingTag && (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center mt-4">
              {t('tags.noTagsYet')}
            </p>
          )}
        </>
      )}
    </div>
  );
};

export default FolderSidebar;
