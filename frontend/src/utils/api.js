// API configuration for different environments
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export const api = {
  baseURL: API_BASE_URL,
  endpoints: {
    // Auth endpoints
    login: `${API_BASE_URL}/auth/login`,
    me: `${API_BASE_URL}/auth/me`,

    // Alumni endpoints
    alumni: `${API_BASE_URL}/alumni`,
    alumniById: (id) => `${API_BASE_URL}/alumni/${id}`,

    // Collection endpoints
    collect: `${API_BASE_URL}/collect`,
    collectStatus: (taskId) => `${API_BASE_URL}/collect/status/${taskId}`,
    manualCollect: `${API_BASE_URL}/manual-collect`,
    uploadNames: `${API_BASE_URL}/upload-names`,

    // Query endpoints
    query: `${API_BASE_URL}/query`,

    // Stats endpoints
    stats: `${API_BASE_URL}/stats`,
    industries: `${API_BASE_URL}/industries`,
    companies: `${API_BASE_URL}/companies`,
    locations: `${API_BASE_URL}/locations`,

    // Dashboard endpoints
    dashboardStats: `${API_BASE_URL}/dashboard/stats`,
    dashboardExport: `${API_BASE_URL}/dashboard/export`,
    dashboardRecent: `${API_BASE_URL}/dashboard/recent`,
    dashboardCollect: `${API_BASE_URL}/dashboard/collect`,

    // Export endpoints
    export: `${API_BASE_URL}/export`,
    recent: `${API_BASE_URL}/recent`,

    // Health check
    health: `${API_BASE_URL}/health`,
  },
};

export default api;
