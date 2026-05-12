import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppRouting } from './hooks/useAppRouting';
import { publicRoutes, authRoutes, protectedRoutes } from './config/routes';

const App: React.FC = () => {
  const { isAuthenticated } = useAppRouting();

  return (
    <Routes>
      {/* Public routes */}
      {publicRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}

      {/* Auth routes with redirect logic */}
      {authRoutes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={
            isAuthenticated ? <Navigate to="/passwords" replace /> : route.element
          }
        />
      ))}

      {/* Protected routes */}
      {protectedRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}
    </Routes>
  );
};

export default App;