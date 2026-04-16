import api from './api';

export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: (refresh) => api.post('/auth/logout', { refresh }),
  getMe: () => api.get('/auth/me'),
};

export const assessmentService = {
  list: () => api.get('/assessments/'),
  detail: (id) => api.get(`/assessments/${id}/`),
  submit: (id, answers) => api.post(`/assessments/${id}/submit`, { answers }),
  getAttempt: (id) => api.get(`/assessments/attempts/${id}/`),
  myAttempts: () => api.get('/assessments/my-attempts/'),
};

export const profileService = {
  // Student Profile
  getStudentProfile: () => api.get('/auth/profiles/student/'),
  updateStudentProfile: (data) => api.put('/auth/profiles/student/', data),
  getStudentProfileDetail: (studentId) => api.get(`/auth/profiles/student/${studentId}/`),

  // Mentor Profile
  getMentorProfile: () => api.get('/auth/profiles/mentor/'),
  updateMentorProfile: (data) => api.put('/auth/profiles/mentor/', data),
  getMentorProfileDetail: (mentorId) => api.get(`/auth/profiles/mentor/${mentorId}/`),
};

export const adminService = {
  getUsers: () => api.get('/auth/admin/users'),
};

export const taskService = {
  // Task list and details
  list: () => api.get('/tasks/', { params: {} }),
  listByDomain: (domain) => api.get('/tasks/', { params: { domain } }),
  detail: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post('/tasks/create/', data),

  // Recommendations
  getRecommendations: () => api.get('/tasks/recommended/'),

  // My tasks
  getMyTasks: (status) => status
    ? api.get('/tasks/my-tasks/', { params: { status } })
    : api.get('/tasks/my-tasks/'),

  // Task assignment management
  getAssignmentDetail: (assignmentId) => api.get(`/tasks/assignments/${assignmentId}/`),
  acceptTask: (assignmentId, accept) => api.post(
    `/tasks/assignments/${assignmentId}/accept/`,
    { accept }
  ),
  updateTaskProgress: (assignmentId, data) => api.put(
    `/tasks/assignments/${assignmentId}/update/`,
    data
  ),
  requestMentorReview: (assignmentId) => api.post(
    `/tasks/assignments/${assignmentId}/request-review/`
  ),

  // Task Completion and Evaluation
  getMCQQuestions: (taskId) => api.get(`/tasks/${taskId}/mcq-questions/`),
  completeTask: (assignmentId, reflectionText) => api.post(
    `/tasks/assignments/${assignmentId}/complete/`,
    { reflective_text: reflectionText }
  ),
  submitMCQAnswers: (completionId, answers, durationSeconds = 0) => api.post(
    `/tasks/completions/${completionId}/submit-mcq/`,
    { student_answers: answers, duration_seconds: durationSeconds }
  ),
  getEvaluation: (evaluationId) => api.get(`/tasks/evaluations/${evaluationId}/`),
  mentorEvaluateTask: (evaluationId, data) => api.post(
    `/tasks/evaluations/${evaluationId}/evaluate/`,
    data
  ),
};

export const mentorService = {
  // Mentor dashboard
  getAssignedStudents: () => api.get('/auth/mentor/assigned-students/'),
  getStudentDetail: (studentId) => api.get(`/auth/mentor/students/${studentId}/`),
  getPendingReviews: () => api.get('/auth/mentor/pending-reviews/'),
  submitReview: (assignmentId, data) => api.post(
    `/auth/mentor/reviews/${assignmentId}/submit/`,
    data
  ),
  autoAssignMentors: () => api.post('/auth/mentor/auto-assign/'),
};

export const analyticsService = {
  // Student analytics
  getStudentAnalytics: () => api.get('/tasks/analytics/student/'),

  // Mentor analytics
  getMentorAnalytics: () => api.get('/tasks/analytics/mentor/'),

  // Admin analytics
  getAdminAnalytics: () => api.get('/tasks/analytics/admin/'),
};
