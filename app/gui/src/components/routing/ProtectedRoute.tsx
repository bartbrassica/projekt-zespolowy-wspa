import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../store/auth';
import LoadingSpinner from '../ui/LoadingSpinner';
import type { ProtectedRouteProps } from '../../types/app';

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;