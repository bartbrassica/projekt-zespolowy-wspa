import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/auth'
import LandingPage from './LandingPage'
import Login from './Login'
import Register from './Register'
import EmailVerification from './EmailVerification'  // Add this import
import Layout from './Layout'
import PasswordManager from './PasswordManager'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route 
        path="/login" 
        element={
          isAuthenticated ? <Navigate to="/passwords" replace /> : <Login />
        } 
      />
      <Route 
        path="/register" 
        element={
          isAuthenticated ? <Navigate to="/passwords" replace /> : <Register />
        } 
      />
      <Route 
        path="/signup" 
        element={<Navigate to="/register" replace />} 
      />
      
      {/* Add email verification route */}
      <Route 
        path="/verify-email" 
        element={<EmailVerification />} 
      />
      
      {/* Password Manager Route */}
      <Route
        path="/passwords"
        element={
          <ProtectedRoute>
            <Layout>
              <PasswordManager />
            </Layout>
          </ProtectedRoute>
        }
      />
      
      {/* Settings route */}
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout>
              <div className="p-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
                <p className="mt-2 text-gray-600 dark:text-gray-400">Your settings page</p>
              </div>
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App