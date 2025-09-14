import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token and Groq API key
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add Groq API key for LLM endpoints
    const groqApiKey = localStorage.getItem('groq_api_key');
    if (groqApiKey && (config.url.includes('/update-dpr') || config.url.includes('/update-dlr') || config.url.includes('/analyze-logs'))) {
      config.headers['X-Groq-API-Key'] = groqApiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  // Get current user info
  getCurrentUser: () => apiClient.get('/user/me'),
  
  // Simple authentication endpoints
  authenticate: (data) => apiClient.post('/auth/authenticate', data),
  completeProfile: (data) => apiClient.post('/auth/complete-profile', data),
  getSimpleUser: () => apiClient.get('/simple-user/me'),
  resetPassword: (data) => apiClient.post('/auth/reset-password', data),
  
  // Google login redirect (handled by backend)
  googleLogin: () => {
    window.location.href = 'http://localhost:8000/auth/google-login';
  },
};

export const documentsAPI = {
  // Get all accessible Google Sheets
  getDocuments: async () => {
    try {
      const response = await apiClient.get('/documents');
      // The backend returns { documents: [...] }, so we need to extract the documents array
      const documents = response.data?.documents || [];
      return {
        ...response,
        data: Array.isArray(documents) ? documents : []
      };
    } catch (error) {
      console.error('Error fetching documents:', error);
      // Return empty array on error
      return { data: [] };
    }
  },
  
  // Get sheet data
  getSheetData: (sheetId, params = {}) => 
    apiClient.get(`/mcp/sheet-data/${sheetId}`, { params }),
  
  // Get column data
  getColumnData: (sheetId, params = {}) => 
    apiClient.get(`/mcp/column-data/${sheetId}`, { params }),
  
  // Get row data
  getRowData: (sheetId, params = {}) => 
    apiClient.get(`/mcp/row-data/${sheetId}`, { params }),
};

export const dprAPI = {
  // Update DPR
  updateDPR: (sheetId, data) => {
    const groqApiKey = localStorage.getItem('groq_api_key');
    const requestData = {
      ...data,
      groq_api_key: groqApiKey
    };
    return apiClient.post(`/update-dpr/${sheetId}`, requestData);
  },
  
  // Update DPR Planned
  updateDPRPlanned: (sheetId, data) => {
    const groqApiKey = localStorage.getItem('groq_api_key');
    const requestData = {
      ...data,
      groq_api_key: groqApiKey
    };
    return apiClient.post(`/update-dpr-planned/${sheetId}`, requestData);
  },
};

export const dlrAPI = {
  // Update DLR
  updateDLR: (sheetId, data) => {
    const groqApiKey = localStorage.getItem('groq_api_key');
    const requestData = {
      ...data,
      groq_api_key: groqApiKey
    };
    return apiClient.post(`/update-dlr/${sheetId}`, requestData);
  },
};

export const logsAPI = {
  // Analyze logs
  analyzeLogs: (sheetId, data) => {
    const groqApiKey = localStorage.getItem('groq_api_key');
    const requestData = {
      ...data,
      groq_api_key: groqApiKey
    };
    return apiClient.post(`/analyze-logs/${sheetId}`, requestData);
  },
};

export const spreadsheetAPI = {
  // Create new spreadsheet
  createNewSpreadsheet: async (data) => {
    try {
      console.log('Creating new spreadsheet with data:', data);
      const response = await apiClient.post('/new-spreadsheet', data);
      console.log('Spreadsheet creation response:', response);
      return response;
    } catch (error) {
      console.error('Spreadsheet creation error:', error);
      console.error('Error response:', error.response?.data);
      throw error;
    }
  },
};

export const workspaceAPI = {
  // Initialize workspace (check and upload DPR_FORMAT if needed)
  initializeWorkspace: () => apiClient.get('/initialize-workspace'),
  
  // Check if DPR_FORMAT exists
  checkDprFormat: () => apiClient.get('/check-dpr-format'),
  
  // Upload DPR_FORMAT
  uploadDprFormat: () => apiClient.post('/upload-dpr-format'),
};

export const chatHistoryAPI = {
  // Get chat history for a user and sheet
  getChatHistory: (mobileNumber, sheetId, date = null) => {
    const url = `/chat-history/${mobileNumber}/${sheetId}${date ? `?date=${date}` : ''}`;
    return apiClient.get(url);
  },
  
  // Save a conversation (user message + assistant response)
  saveConversation: (data) => apiClient.post('/chat-history/save', data),
  
  // Get available conversation dates
  getChatDates: (mobileNumber, sheetId) => 
    apiClient.get(`/chat-history/${mobileNumber}/${sheetId}/dates`),
  
  // Clear all chat history for a user and sheet
  clearChatHistory: (mobileNumber, sheetId) => 
    apiClient.delete(`/chat-history/${mobileNumber}/${sheetId}`),
  
  // Clear chat history for a specific date
  clearChatHistoryByDate: (mobileNumber, sheetId, date) => 
    apiClient.delete(`/chat-history/${mobileNumber}/${sheetId}/date/${date}`),
};

export default apiClient;
