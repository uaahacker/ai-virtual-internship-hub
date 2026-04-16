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

// Task pages
import RecommendedTasksPage from './pages/RecommendedTasksPage';
import MyTasksPage from './pages/MyTasksPage';
import TaskCompletionPage from './pages/TaskCompletionPage';
import TaskMCQQuizPage from './pages/TaskMCQQuizPage';
import TaskEvaluationResultPage from './pages/TaskEvaluationResultPage';

// Portfolio pages
import PortfolioPage from './pages/PortfolioPage';
import PortfolioItemDetailPage from './pages/PortfolioItemDetailPage';

// Mentor pages
import MentorAssignedStudentsPage from './pages/MentorAssignedStudentsPage';
import MentorStudentDetailPage from './pages/MentorStudentDetailPage';
import MentorPendingReviewsPage from './pages/MentorPendingReviewsPage';
import MentorReviewTaskPage from './pages/MentorReviewTaskPage';

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
      <Route path="/student/tasks/recommended" element={<ProtectedRoute role="Student"><RecommendedTasksPage /></ProtectedRoute>} />
      <Route path="/student/tasks/my-tasks" element={<ProtectedRoute role="Student"><MyTasksPage /></ProtectedRoute>} />
      <Route path="/student/tasks/complete/:assignmentId" element={<ProtectedRoute role="Student"><TaskCompletionPage /></ProtectedRoute>} />
      <Route path="/student/tasks/mcq/:completionId/:taskId" element={<ProtectedRoute role="Student"><TaskMCQQuizPage /></ProtectedRoute>} />
      <Route path="/student/tasks/evaluation/:evaluationId" element={<ProtectedRoute role="Student"><TaskEvaluationResultPage /></ProtectedRoute>} />
      <Route path="/student/portfolio" element={<ProtectedRoute role="Student"><PortfolioPage /></ProtectedRoute>} />
      <Route path="/student/portfolio/items/:itemId" element={<ProtectedRoute role="Student"><PortfolioItemDetailPage /></ProtectedRoute>} />

      {/* Mentor routes */}
      <Route path="/mentor/dashboard" element={<ProtectedRoute role="Mentor"><MentorDashboard /></ProtectedRoute>} />
      <Route path="/mentor/students" element={<ProtectedRoute role="Mentor"><MentorAssignedStudentsPage /></ProtectedRoute>} />
      <Route path="/mentor/students/:studentId" element={<ProtectedRoute role="Mentor"><MentorStudentDetailPage /></ProtectedRoute>} />
      <Route path="/mentor/reviews" element={<ProtectedRoute role="Mentor"><MentorPendingReviewsPage /></ProtectedRoute>} />
      <Route path="/mentor/reviews/:assignmentId" element={<ProtectedRoute role="Mentor"><MentorReviewTaskPage /></ProtectedRoute>} />

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
