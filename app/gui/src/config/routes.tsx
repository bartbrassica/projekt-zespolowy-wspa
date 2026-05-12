import React from 'react';
import { Navigate } from 'react-router-dom';
import LandingPage from '../LandingPage';
import Login from '../Login';
import Register from '../Register';
import EmailVerification from '../EmailVerification';
import ForgotPassword from '../ForgotPassword';
import ResetPassword from '../ResetPassword';
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
    path: '/reset-password',
    element: <ResetPassword />
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
  },
  {
    path: '/forgot-password',
    element: <ForgotPassword />
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