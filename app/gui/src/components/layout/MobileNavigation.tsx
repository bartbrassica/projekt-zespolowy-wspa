import React from 'react';
import { Link } from 'react-router-dom';
import type { NavigationProps } from '../../types/layout';

const MobileNavigation: React.FC<NavigationProps> = ({ items, currentPath }) => {
  return (
    <div className="sm:hidden">
      <div className="pt-2 pb-3 space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                isActive
                  ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500 text-indigo-700 dark:text-indigo-300'
                  : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 hover:text-gray-800 dark:hover:text-white'
              }`}
            >
              <div className="flex items-center">
                <Icon className="h-4 w-4 mr-2" />
                {item.name}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default MobileNavigation;