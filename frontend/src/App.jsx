import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Auth pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Dashboard pages
import StudentDashboard from './pages/StudentDashboard';
import MentorDashboard from './pages/MentorDashboard';
import AdminDashboard from './pages/AdminDashboard';

// Assessment pages
import AssessmentList from './pages/AssessmentList';
import TakeAssessment from './pages/TakeAssessment';
import AssessmentResult from './pages/AssessmentResult';

// Guards
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to={getDashboardPath(user.role)} />} />
      <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to={getDashboardPath(user.role)} />} />

      {/* Student routes */}
      <Route path="/student/dashboard" element={<ProtectedRoute role="Student"><StudentDashboard /></ProtectedRoute>} />
      <Route path="/student/assessments" element={<ProtectedRoute role="Student"><AssessmentList /></ProtectedRoute>} />
      <Route path="/student/assessments/:id" element={<ProtectedRoute role="Student"><TakeAssessment /></ProtectedRoute>} />
      <Route path="/student/results/:attemptId" element={<ProtectedRoute role="Student"><AssessmentResult /></ProtectedRoute>} />

      {/* Mentor routes */}
      <Route path="/mentor/dashboard" element={<ProtectedRoute role="Mentor"><MentorDashboard /></ProtectedRoute>} />

      {/* Admin routes */}
      <Route path="/admin/dashboard" element={<ProtectedRoute role="Admin"><AdminDashboard /></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

function getDashboardPath(role) {
  switch (role) {
    case 'Student': return '/student/dashboard';
    case 'Mentor': return '/mentor/dashboard';
    case 'Admin': return '/admin/dashboard';
    default: return '/login';
  }
}

export default App;
