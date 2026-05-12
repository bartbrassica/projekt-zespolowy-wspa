import React from 'react';
import { useAuth } from './store/auth';
import { useLayoutActions } from './hooks/useLayoutActions';
import Header from './components/layout/Header';
import type { LayoutProps } from './types/layout';

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const { handleLogout } = useLayoutActions();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} onLogout={handleLogout} />
      <main>
        <div className="w-full">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;