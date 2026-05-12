import React from 'react';
import { Navigate } from 'react-router-dom';
import LandingPage from '../LandingPage';
import Login from '../Login';
import Register from '../Register';
import EmailVerification from '../EmailVerification';
import Layout from '../Layout';
import PasswordManager from '../PasswordManager';
import SettingsPage from '../components/pages/SettingsPage';
import ProtectedRoute from '../components/routing/ProtectedRoute';

export const createRouteElement = (Component: React.ComponentType, isProtected = false, withLayout = false) => {
  let element = <Component />;

  if (withLayout) {
    element = <Layout>{element}</Layout>;
  }

  if (isProtected) {
    element = <ProtectedRoute>{element}</ProtectedRoute>;
  }

  return element;
};

export const publicRoutes = [
  {
    path: '/',
    element: <LandingPage />
  },
  {
    path: '/verify-email',
    element: <EmailVerification />
  },
  {
    path: '/signup',
    element: <Navigate to="/register" replace />
  },
  {
    path: '*',
    element: <Navigate to="/" replace />
  }
];

export const authRoutes = [
  {
    path: '/login',
    element: <Login />
  },
  {
    path: '/register',
    element: <Register />
  }
];

export const protectedRoutes = [
  {
    path: '/passwords',
    element: createRouteElement(PasswordManager, true, true)
  },
  {
    path: '/settings',
    element: createRouteElement(SettingsPage, true, true)
  }
];