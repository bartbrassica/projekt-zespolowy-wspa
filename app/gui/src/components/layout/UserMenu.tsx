import React from 'react';
import { LogOut } from 'lucide-react';
import type { UserMenuProps } from '../../types/layout';

const UserMenu: React.FC<UserMenuProps> = ({ user, onLogout }) => {
  return (
    <div className="flex items-center">
      <span className="text-sm text-gray-700 dark:text-gray-300 mr-4">
        {user?.email}
      </span>
      <button
        onClick={onLogout}
        className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 dark:text-gray-300 bg-white dark:bg-gray-800 hover:text-gray-700 dark:hover:text-white focus:outline-none transition"
      >
        <LogOut className="h-4 w-4 mr-2" />
        Sign out
      </button>
    </div>
  );
};

export default UserMenu;