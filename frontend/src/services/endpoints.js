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

export const adminService = {
  getUsers: () => api.get('/auth/admin/users'),
};
