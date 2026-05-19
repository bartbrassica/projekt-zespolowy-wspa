import React, { useState } from 'react';
import { Tag as TagIcon, Plus, X } from 'lucide-react';
import type { Tag } from '../../types/password';

interface TagSelectorProps {
  tags: Tag[];
  selectedTagIds: string[];
  onChange: (tagIds: string[]) => void;
  onCreateTag?: (name: string, color?: string) => Promise<void>;
  label?: string;
}

export const TagSelector: React.FC<TagSelectorProps> = ({
  tags,
  selectedTagIds,
  onChange,
  onCreateTag,
  label = 'Tags'
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#6366f1');

  const handleToggleTag = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter(id => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagName.trim() || !onCreateTag) return;

    await onCreateTag(newTagName.trim(), newTagColor);
    setNewTagName('');
    setNewTagColor('#6366f1');
    setIsCreating(false);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        <TagIcon className="inline h-4 w-4 mr-1" />
        {label}
      </label>

      <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white dark:bg-gray-700">
        {tags.length === 0 && !isCreating && (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-2">
            No tags yet. Create one below!
          </p>
        )}

        <div className="flex flex-wrap gap-2 mb-2">
          {tags.map((tag) => {
            const isSelected = selectedTagIds.includes(tag.id);
            return (
              <button
                key={tag.id}
                type="button"
                onClick={() => handleToggleTag(tag.id)}
                className={`inline-flex items-center px-2.5 py-1 rounded text-sm font-medium transition-all ${
                  isSelected
                    ? 'ring-2 ring-indigo-500 ring-offset-1'
                    : 'opacity-60 hover:opacity-100'
                }`}
                style={{
                  backgroundColor: tag.color ? `${tag.color}30` : '#e5e7eb',
                  color: tag.color || '#6b7280',
                  borderLeft: `3px solid ${tag.color || '#9ca3af'}`
                }}
              >
                {tag.name}
                {isSelected && <span className="ml-1 text-xs">✓</span>}
              </button>
            );
          })}
        </div>

        {isCreating ? (
          <form onSubmit={handleCreateTag} className="flex gap-2 items-end mt-2">
            <div className="flex-1">
              <input
                type="text"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                placeholder="Tag name"
                className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                autoFocus
                maxLength={50}
              />
            </div>
            <div>
              <input
                type="color"
                value={newTagColor}
                onChange={(e) => setNewTagColor(e.target.value)}
                className="h-8 w-8 border border-gray-300 dark:border-gray-600 rounded cursor-pointer"
                title="Tag color"
              />
            </div>
            <button
              type="submit"
              className="px-2 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false);
                setNewTagName('');
                setNewTagColor('#6366f1');
              }}
              className="px-2 py-1 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500 text-sm"
            >
              <X className="h-4 w-4" />
            </button>
          </form>
        ) : (
          onCreateTag && (
            <button
              type="button"
              onClick={() => setIsCreating(true)}
              className="w-full mt-2 px-2 py-1.5 border border-dashed border-gray-300 dark:border-gray-600 rounded text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:border-indigo-300 dark:hover:border-indigo-600 transition-colors flex items-center justify-center gap-1"
            >
              <Plus className="h-4 w-4" />
              Create new tag
            </button>
          )
        )}
      </div>
    </div>
  );
};

export default TagSelector;
