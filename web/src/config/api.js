// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  VERSION: import.meta.env.VITE_API_VERSION || 'v1',
};

// API Endpoints
export const API_ENDPOINTS = {
  EXECUTE_STREAM: `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}/agent/tasks/execute-stream`,
};

// Build complete API URLs
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}${endpoint}`;
};