import React from 'react';
import {
  Star,
  StarOff,
  ExternalLink,
  Clock,
  Copy,
  Eye,
  EyeOff,
  Edit,
  Trash2,
  Folder,
  Tag,
  Share2
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { PasswordCardProps } from '../../types/password';
import { getSiteHostname, formatDate } from '../../utils/passwordUtils';

const PasswordCard: React.FC<PasswordCardProps> = ({
  entry,
  showPassword,
  decryptedPassword,
  onToggleFavorite,
  onCopyPassword,
  onToggleVisibility,
  onEdit,
  onDelete,
  onShare
}) => {
  const { t } = useTranslation();
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {entry.name}
          </h3>
          {entry.is_favorite && (
            <Star className="h-4 w-4 text-yellow-500 fill-current" />
          )}
        </div>
        <button
          onClick={() => onToggleFavorite(entry)}
          className="text-gray-400 hover:text-yellow-500 transition-colors"
        >
          {entry.is_favorite ? (
            <StarOff className="h-5 w-5" />
          ) : (
            <Star className="h-5 w-5" />
          )}
        </button>
      </div>

      <div className="space-y-2 mb-4">
        {entry.site && (
          <div className="flex items-center gap-2 text-sm">
            <ExternalLink className="h-4 w-4 text-gray-400" />
            <a
              href={entry.site}
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 hover:text-indigo-700 truncate"
            >
              {getSiteHostname(entry.site)}
            </a>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <span className="font-medium">{t('passwordCard.username')}</span>
          <span className="truncate">{entry.username || t('passwordCard.notAvailable')}</span>
        </div>

        {entry.folder && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Folder className="h-4 w-4" />
            <span className="truncate">
              {entry.folder.icon && `${entry.folder.icon} `}
              {entry.folder.name}
            </span>
          </div>
        )}

        {entry.tags && entry.tags.length > 0 && (
          <div className="flex items-start gap-2 text-sm">
            <Tag className="h-4 w-4 text-gray-400 mt-0.5" />
            <div className="flex flex-wrap gap-1.5">
              {entry.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  style={{
                    backgroundColor: tag.color ? `${tag.color}20` : '#e5e7eb',
                    color: tag.color || '#6b7280',
                    borderLeft: `3px solid ${tag.color || '#9ca3af'}`
                  }}
                >
                  {tag.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {entry.expires_at && (
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-yellow-500" />
            <span className="text-yellow-600 dark:text-yellow-400">
              {t('passwordCard.expires')} {formatDate(entry.expires_at)}
            </span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onCopyPassword(entry.id)}
          className="flex-1 px-3 py-1.5 text-sm bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded hover:bg-indigo-100 dark:hover:bg-indigo-900/30 transition-colors flex items-center justify-center gap-1"
        >
          <Copy className="h-4 w-4" />
          {t('passwordCard.copy')}
        </button>
        <button
          onClick={() => onToggleVisibility(entry.id)}
          className="px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          {showPassword ? (
            <EyeOff className="h-4 w-4" />
          ) : (
            <Eye className="h-4 w-4" />
          )}
        </button>
        <button
          onClick={() => onEdit(entry)}
          className="px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          <Edit className="h-4 w-4" />
        </button>
        <button
          onClick={() => onShare(entry)}
          className="px-3 py-1.5 text-sm bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
          title={t('passwordCard.sharePassword')}
        >
          <Share2 className="h-4 w-4" />
        </button>
        <button
          onClick={() => onDelete(entry.id)}
          className="px-3 py-1.5 text-sm bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {showPassword && decryptedPassword && (
        <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('passwordCard.password')}</p>
          <code className="text-sm font-mono text-gray-900 dark:text-white">
            {decryptedPassword}
          </code>
        </div>
      )}
    </div>
  );
};

export default PasswordCard;