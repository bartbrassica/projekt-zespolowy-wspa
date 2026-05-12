import React from 'react';
import { useLocation } from 'react-router-dom';
import BrandLogo from './BrandLogo';
import Navigation from './Navigation';
import MobileNavigation from './MobileNavigation';
import UserMenu from './UserMenu';
import { navigationItems } from '../../config/navigation';
import type { HeaderProps } from '../../types/layout';

const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  const location = useLocation();

  return (
    <nav className="bg-white dark:bg-gray-800 shadow">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <BrandLogo />
            <Navigation items={navigationItems} currentPath={location.pathname} />
          </div>
          <UserMenu user={user} onLogout={onLogout} />
        </div>
      </div>
      <MobileNavigation items={navigationItems} currentPath={location.pathname} />
    </nav>
  );
};

export default Header;