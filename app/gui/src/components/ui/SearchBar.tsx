import React from 'react';
import { Search, Plus } from 'lucide-react';
import type { SearchBarProps } from '../../types/password';

const SearchBar: React.FC<SearchBarProps> = ({ value, onChange, onAddPassword }) => {
  return (
    <div className="mb-6 flex flex-col sm:flex-row gap-4">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search passwords..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
      <button
        onClick={onAddPassword}
        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
      >
        <Plus className="h-5 w-5" />
        Add Password
      </button>
    </div>
  );
};

export default SearchBar;