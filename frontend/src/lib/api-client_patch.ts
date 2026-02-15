// Helper to get cookie value
function getCookie(name: string): string | null {
  const value = \;  + '$' + {document.cookie}\;
  const parts = value.split(\;  + '$' + {name}=\);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Request interceptor for adding auth token and CSRF token
apiClient.interceptors.request.use(
  (config) => {
    // Add Bearer token
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = \Bearer  + '$' + {token}\;
    }
    
    // Add CSRF token from cookie (Double Submit Cookie pattern)
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
    
    return config;
  },
