/**
 * EduPilot AI — API Client Module
 * Sends auth token with every request.
 */
const API_BASE = window.location.origin;

const api = {
  async request(method, path, body = null) {
    const token = localStorage.getItem('edupilot-token') || '';
    const opts = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      }
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (!res.ok) {
      if (res.status === 401) { window.location.href = '/'; return; }
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Request failed');
    }
    return res.json();
  },

  // Students
  getStudents: ()          => api.request('GET', '/api/students'),
  getStudent:  (id)        => api.request('GET', `/api/students/${id}`),
  createStudent: (data)    => api.request('POST', '/api/students', data),
  updateStudent: (id,data) => api.request('PUT', `/api/students/${id}`, data),
  deleteStudent: (id)      => api.request('DELETE', `/api/students/${id}`),

  // Predictions
  predict:       (id) => api.request('POST', `/api/predict/${id}`),
  getWeaknesses: (id) => api.request('GET', `/api/weaknesses/${id}`),

  // Plans
  generatePlan:     (id, hours=4) => api.request('POST', `/api/plans/${id}?available_hours=${hours}`),
  getPlan:          (id) => api.request('GET', `/api/plans/${id}`),
  adaptPlan:        (id) => api.request('POST', `/api/plans/${id}/adapt`),
  getRecommendations:(id)=> api.request('GET', `/api/plans/${id}/recommendations`),

  // Progress
  logProgress:       (id,data) => api.request('POST', `/api/progress/${id}`, data),
  getProgress:       (id,days=30) => api.request('GET', `/api/progress/${id}?days=${days}`),
  getStreak:         (id) => api.request('GET', `/api/progress/${id}/streak`),
  getProgressAnalysis:(id)=> api.request('GET', `/api/progress/${id}/analysis`),

  // Analytics
  getOverview:  (id) => api.request('GET', `/api/analytics/${id}/overview`),
  getTrends:    (id) => api.request('GET', `/api/analytics/${id}/trends`),
  getHeatmap:   (id) => api.request('GET', `/api/analytics/${id}/heatmap`),
};

window.api = api;
