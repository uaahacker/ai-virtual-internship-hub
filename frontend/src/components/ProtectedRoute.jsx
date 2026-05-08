import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (role && user.role !== role) {
    // Redirect to their own dashboard
    const dashPath = {
      Student: '/student/dashboard',
      Mentor: '/mentor/dashboard',
      Admin: '/admin/dashboard',
    };
    console.log('🔍 ProtectedRoute - wrong role, redirecting to:', dashPath[user.role]);
    return <Navigate to={dashPath[user.role] || '/login'} replace />;
  }

  return children;
}
