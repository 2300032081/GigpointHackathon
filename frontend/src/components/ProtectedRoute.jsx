import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div className="auth-loading">Loading your store...</div>
  return isAuthenticated ? children : <Navigate to="/signin" replace state={{ from: location.pathname }} />
}
