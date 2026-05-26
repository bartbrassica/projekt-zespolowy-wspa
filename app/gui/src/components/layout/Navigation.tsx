import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { NavigationProps } from '../../types/layout';

const Navigation: React.FC<NavigationProps> = ({ items, currentPath }) => {
  const { t } = useTranslation();

  return (
    <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = currentPath === item.href;
        return (
          <Link
            key={item.name}
            to={item.href}
            className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
              isActive
                ? 'border-indigo-500 text-gray-900 dark:text-white'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
            }`}
          >
            <Icon className="h-4 w-4 mr-2" />
            {t(item.name)}
          </Link>
        );
      })}
    </div>
  );
};

export default Navigation;