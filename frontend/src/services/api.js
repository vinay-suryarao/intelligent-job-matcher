// ========================================
// API SERVICE - REAL-TIME BACKEND CONNECTION
// ========================================

const API_BASE_URL = 'http://localhost:8000/api';

// Get token and user_id from localStorage
const getToken = () => localStorage.getItem('token');
const getUserId = () => localStorage.getItem('user_id');

// Helper function for API calls
const apiCall = async (endpoint, options = {}) => {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = getToken();
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`❌ API Error [${endpoint}]:`, data);
      return { error: data.detail || 'API request failed', status: response.status };
    }

    console.log(`✅ API Success [${endpoint}]:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Network Error [${endpoint}]:`, error);
    return { error: 'Network error. Is backend running?', networkError: true };
  }
};

const api = {
  // ========================================
  // HEALTH CHECK
  // ========================================

  healthCheck: async () => {
    return await apiCall('/health');
  },

  // ========================================
  // AUTH ENDPOINTS
  // ========================================

  login: async (email, password) => {
    return await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (email, password, fullName) => {
    return await apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  },

  // ========================================
  // USER PROFILE ENDPOINTS
  // ========================================

  getProfile: async () => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };
    return await apiCall(`/users/${userId}`);
  },

  updateProfile: async (profileData) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };
    return await apiCall(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  // Forgot Password
  forgotPassword: async (email) => {
    return await apiCall('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  uploadResume: async (file) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };

    const formData = new FormData();
    formData.append('file', file);

    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/auth/upload-resume/${userId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    return response.json();
  },

  // ========================================
  // JOBS ENDPOINTS (REAL-TIME)
  // ========================================

  getJobs: async (limit = 50, skip = 0) => {
    return await apiCall(`/jobs/list?limit=${limit}&skip=${skip}`);
  },

  getJobById: async (jobId) => {
    return await apiCall(`/jobs/${jobId}`);
  },

  searchJobs: async (keyword, location = 'India', limit = 20) => {
    return await apiCall(`/jobs/search?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}&limit=${limit}`);
  },

  scrapeNewJobs: async (keyword, location = 'India') => {
    return await apiCall('/jobs/scrape-jobs', {
      method: 'POST',
      body: JSON.stringify({
        keywords: keyword,
        location: location,
        max_results_per_source: 20,
      }),
    });
  },

  // ========================================
  // INTERNSHIPS ENDPOINTS (REAL-TIME)
  // ========================================

  getInternships: async (limit = 50, skip = 0) => {
    return await apiCall(`/internships/list?limit=${limit}&skip=${skip}`);
  },

  getInternshipById: async (internshipId) => {
    return await apiCall(`/internships/${internshipId}`);
  },

  searchInternships: async (keyword, location = 'India', limit = 20) => {
    return await apiCall(`/internships/search?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}&limit=${limit}`);
  },

  // ========================================
  // MATCHING ENDPOINTS (AI-POWERED REAL-TIME)
  // ========================================

  getJobMatches: async (limit = 10) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in', matches: [] };

    return await apiCall('/matching/matches', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        match_type: 'jobs',
        limit: limit,
      }),
    });
  },

  getInternshipMatches: async (limit = 10) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in', matches: [] };

    return await apiCall('/matching/matches', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        match_type: 'internships',
        limit: limit,
      }),
    });
  },

  getAllMatches: async (limit = 20) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in', matches: [] };

    return await apiCall('/matching/matches', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        match_type: 'all',
        limit: limit,
      }),
    });
  },

  // ========================================
  // STATISTICS ENDPOINTS (REAL-TIME)
  // ========================================

  getStatistics: async () => {
    return await apiCall('/statistics/overview');
  },

  getUserStats: async () => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };
    return await apiCall(`/statistics/user/${userId}`);
  },

  getSkillsAnalysis: async () => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };
    return await apiCall(`/statistics/skills-analysis/${userId}`);
  },

  // ========================================
  // CHAT ENDPOINTS
  // ========================================

  sendChatMessage: async (message, history = []) => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in' };

    return await apiCall('/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        message: message,
        messages: history
      }),
    });
  },

  getChatHistory: async () => {
    const userId = getUserId();
    if (!userId) return { error: 'User not logged in', messages: [] };
    return await apiCall(`/chat/history/${userId}`);
  },

  // ========================================
  // SCHEDULER STATUS
  // ========================================

  getSchedulerStatus: async () => {
    return await apiCall('/jobs/scheduler/status');
  },

  triggerScrapeNow: async () => {
    return await apiCall('/jobs/scheduler/trigger-now', {
      method: 'POST',
    });
  },
};

export default api;