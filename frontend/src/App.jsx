import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Landing page
import LandingPage from './pages/LandingPage';

// Auth pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

// Dashboard pages
import StudentDashboard from './pages/StudentDashboard';
import MentorDashboard from './pages/MentorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminAssessmentsPage from './pages/AdminAssessmentsPage';
import AdminTasksPage from './pages/AdminTasksPage';

// Analytics pages
import StudentAnalyticsDashboard from './pages/StudentAnalyticsDashboard';
import MentorAnalyticsDashboard from './pages/MentorAnalyticsDashboard';
import AdminAnalyticsDashboard from './pages/AdminAnalyticsDashboard';

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
import TextSubmissionPage from './pages/TextSubmissionPage';

// Portfolio pages
import PortfolioPage from './pages/PortfolioPage';
import PortfolioItemDetailPage from './pages/PortfolioItemDetailPage';

// Chat page
import ChatPage from './pages/ChatPage';

// Mentor pages
import MentorAssignedStudentsPage from './pages/MentorAssignedStudentsPage';
import MentorStudentDetailPage from './pages/MentorStudentDetailPage';
import MentorPendingReviewsPage from './pages/MentorPendingReviewsPage';
import MentorReviewTaskPage from './pages/MentorReviewTaskPage';
import MentorSelectStudentsPage from './pages/MentorSelectStudentsPage';
import MentorChatPage from './pages/MentorChatPage';
import MentorTasksPage from './pages/MentorTasksPage';
import MentorCreateTaskPage from './pages/MentorCreateTaskPage';
import MentorTaskMCQPage from './pages/MentorTaskMCQPage';

// New feature pages
import AnnouncementsPage from './pages/AnnouncementsPage';
import DirectChatPage from './pages/DirectChatPage';
import NotificationsPage from './pages/NotificationsPage';
import GoogleOnboardingPage from './pages/GoogleOnboardingPage';

// Settings pages
import StudentSettingsPage from './pages/StudentSettingsPage';
import MentorSettingsPage from './pages/MentorSettingsPage';

// Guards
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  try {
    const { user, loading } = useAuth();

    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-600/20 mb-4">
              <div className="w-8 h-8 border-3 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      );
    }

    return (
      <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to={getDashboardPath(user.role)} />} />
      <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to={getDashboardPath(user.role)} />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/google-onboarding" element={<GoogleOnboardingPage />} />

      {/* Student routes */}
      <Route path="/student/dashboard" element={<ProtectedRoute role="Student"><StudentDashboard /></ProtectedRoute>} />
      <Route path="/student/analytics" element={<ProtectedRoute role="Student"><StudentAnalyticsDashboard /></ProtectedRoute>} />
      <Route path="/student/assessments" element={<ProtectedRoute role="Student"><AssessmentList /></ProtectedRoute>} />
      <Route path="/student/assessments/:id" element={<ProtectedRoute role="Student"><TakeAssessment /></ProtectedRoute>} />
      <Route path="/student/results/:attemptId" element={<ProtectedRoute role="Student"><AssessmentResult /></ProtectedRoute>} />
      <Route path="/student/tasks/recommended" element={<ProtectedRoute role="Student"><RecommendedTasksPage /></ProtectedRoute>} />
      <Route path="/student/tasks/my-tasks" element={<ProtectedRoute role="Student"><MyTasksPage /></ProtectedRoute>} />
      <Route path="/student/tasks/complete/:assignmentId" element={<ProtectedRoute role="Student"><TaskCompletionPage /></ProtectedRoute>} />
      <Route path="/student/tasks/submit-text/:assignmentId" element={<ProtectedRoute role="Student"><TextSubmissionPage /></ProtectedRoute>} />
      <Route path="/student/tasks/mcq/:completionId/:taskId" element={<ProtectedRoute role="Student"><TaskMCQQuizPage /></ProtectedRoute>} />
      <Route path="/student/tasks/evaluation/:evaluationId" element={<ProtectedRoute role="Student"><TaskEvaluationResultPage /></ProtectedRoute>} />
      <Route path="/student/portfolio" element={<ProtectedRoute role="Student"><PortfolioPage /></ProtectedRoute>} />
      <Route path="/student/chat" element={<ProtectedRoute role="Student"><ChatPage /></ProtectedRoute>} />
      <Route path="/student/portfolio/items/:itemId" element={<ProtectedRoute role="Student"><PortfolioItemDetailPage /></ProtectedRoute>} />
      <Route path="/student/settings" element={<ProtectedRoute role="Student"><StudentSettingsPage /></ProtectedRoute>} />
      <Route path="/student/announcements" element={<ProtectedRoute role="Student"><AnnouncementsPage /></ProtectedRoute>} />
      <Route path="/student/mentor-chat" element={<ProtectedRoute role="Student"><DirectChatPage /></ProtectedRoute>} />
      <Route path="/student/notifications" element={<ProtectedRoute role="Student"><NotificationsPage /></ProtectedRoute>} />

      {/* Mentor routes */}
      <Route path="/mentor/dashboard" element={<ProtectedRoute role="Mentor"><MentorDashboard /></ProtectedRoute>} />
      <Route path="/mentor/analytics" element={<ProtectedRoute role="Mentor"><MentorAnalyticsDashboard /></ProtectedRoute>} />
      <Route path="/mentor/students" element={<ProtectedRoute role="Mentor"><MentorAssignedStudentsPage /></ProtectedRoute>} />
      <Route path="/mentor/students/:studentId" element={<ProtectedRoute role="Mentor"><MentorStudentDetailPage /></ProtectedRoute>} />
      <Route path="/mentor/reviews" element={<ProtectedRoute role="Mentor"><MentorPendingReviewsPage /></ProtectedRoute>} />
      <Route path="/mentor/reviews/:assignmentId" element={<ProtectedRoute role="Mentor"><MentorReviewTaskPage /></ProtectedRoute>} />
      <Route path="/mentor/select-students" element={<ProtectedRoute role="Mentor"><MentorSelectStudentsPage /></ProtectedRoute>} />
      <Route path="/mentor/chat" element={<ProtectedRoute role="Mentor"><MentorChatPage /></ProtectedRoute>} />
      <Route path="/mentor/tasks" element={<ProtectedRoute role="Mentor"><MentorTasksPage /></ProtectedRoute>} />
      <Route path="/mentor/tasks/create" element={<ProtectedRoute role="Mentor"><MentorCreateTaskPage /></ProtectedRoute>} />
      <Route path="/mentor/tasks/:taskId/edit" element={<ProtectedRoute role="Mentor"><MentorCreateTaskPage /></ProtectedRoute>} />
      <Route path="/mentor/tasks/:taskId/quiz" element={<ProtectedRoute role="Mentor"><MentorTaskMCQPage /></ProtectedRoute>} />
      <Route path="/mentor/settings" element={<ProtectedRoute role="Mentor"><MentorSettingsPage /></ProtectedRoute>} />
      <Route path="/mentor/announcements" element={<ProtectedRoute role="Mentor"><AnnouncementsPage /></ProtectedRoute>} />
      <Route path="/mentor/students/:studentId/chat" element={<ProtectedRoute role="Mentor"><DirectChatPage /></ProtectedRoute>} />
      <Route path="/mentor/notifications" element={<ProtectedRoute role="Mentor"><NotificationsPage /></ProtectedRoute>} />

      {/* Admin routes */}
      <Route path="/admin/dashboard" element={<ProtectedRoute role="Admin"><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/analytics" element={<ProtectedRoute role="Admin"><AdminAnalyticsDashboard /></ProtectedRoute>} />
      <Route path="/admin/announcements" element={<ProtectedRoute role="Admin"><AnnouncementsPage /></ProtectedRoute>} />
      <Route path="/admin/users" element={<ProtectedRoute role="Admin"><AdminUsersPage /></ProtectedRoute>} />
      <Route path="/admin/assessments" element={<ProtectedRoute role="Admin"><AdminAssessmentsPage /></ProtectedRoute>} />
      <Route path="/admin/tasks" element={<ProtectedRoute role="Admin"><AdminTasksPage /></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
    );
  } catch (err) {
    console.error('App rendering error:', err);
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-center">
          <p className="text-red-600 font-semibold mb-2">App Error</p>
          <p className="text-gray-600 text-sm">{err.message}</p>
        </div>
      </div>
    );
  }
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
