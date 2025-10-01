import axios from 'axios';
import { API_CONFIG, TIMEOUT_CONFIG, STORAGE_KEYS } from '../constants/api.js';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: TIMEOUT_CONFIG.DEFAULT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management utilities
const tokenManager = {
  getAccessToken: () => localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN),
  getRefreshToken: () => localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN),
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    if (refreshToken) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    }
  },
  clearTokens: () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_PROFILE);
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenManager.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Attempt to refresh token
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.REFRESH}`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        tokenManager.setTokens(access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        tokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Generic HTTP methods
  get: (url, config = {}) => api.get(url, config),
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  patch: (url, data = {}, config = {}) => api.patch(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),

  // Authentication methods
  auth: {
    login: (credentials) =>
      api.post(API_CONFIG.ENDPOINTS.AUTH.LOGIN, credentials),
    
    register: (userData) =>
      api.post(API_CONFIG.ENDPOINTS.AUTH.REGISTER, userData),
    
    refreshToken: (refreshToken) =>
      api.post(API_CONFIG.ENDPOINTS.AUTH.REFRESH, { refresh: refreshToken }),
    
    verifyToken: (token) =>
      api.post(API_CONFIG.ENDPOINTS.AUTH.VERIFY, { token }),
    
    getProfile: () =>
      api.get(API_CONFIG.ENDPOINTS.AUTH.PROFILE),
    
    updateProfile: (data) =>
      api.put(API_CONFIG.ENDPOINTS.AUTH.PROFILE, data),
    
    changePassword: (passwordData) =>
      api.post(API_CONFIG.ENDPOINTS.AUTH.CHANGE_PASSWORD, passwordData),
    
    getUserStats: () =>
      api.get(API_CONFIG.ENDPOINTS.AUTH.STATS),
  },

  // Diary methods
  diary: {
    startSession: (sessionData) =>
      api.post(API_CONFIG.ENDPOINTS.DIARY.START_SESSION, sessionData),
    
    respond: (responseData) =>
      api.post(API_CONFIG.ENDPOINTS.DIARY.RESPOND, responseData),
    
    complete: (completionData = {}) =>
      api.post(API_CONFIG.ENDPOINTS.DIARY.COMPLETE, completionData),
    
    getEntries: (page = 1, pageSize = 20) =>
      api.get(`${API_CONFIG.ENDPOINTS.DIARY.ENTRIES}?page=${page}&page_size=${pageSize}`),
    
    getEntryDetail: (entryId) =>
      api.get(`${API_CONFIG.ENDPOINTS.DIARY.ENTRY_DETAIL}/${entryId}`),
    
    getEntry: (entryId) =>
      api.get(`${API_CONFIG.ENDPOINTS.DIARY.ENTRY_DETAIL}/${entryId}`),
    
    getWellbeingCheck: (daysBack = 14) =>
      api.get(`${API_CONFIG.ENDPOINTS.DIARY.WELLBEING_CHECK}?days_back=${daysBack}`, {
        timeout: TIMEOUT_CONFIG.ANALYTICS,
      }),
    
    getStats: () =>
      api.get(API_CONFIG.ENDPOINTS.DIARY.STATS),
    
    getEmotions: () =>
      api.get(API_CONFIG.ENDPOINTS.DIARY.EMOTIONS),
    
    getQuestionInsights: () =>
      api.get(API_CONFIG.ENDPOINTS.DIARY.QUESTION_INSIGHTS),
    
    // Advanced Analytics (Phase 3)
    predictMood: (predictionData) =>
      api.post(API_CONFIG.ENDPOINTS.DIARY.PREDICT_MOOD, predictionData, {
        timeout: TIMEOUT_CONFIG.ANALYTICS,
      }),
    
    getRecommendations: () =>
      api.get(API_CONFIG.ENDPOINTS.DIARY.RECOMMENDATIONS, {
        timeout: TIMEOUT_CONFIG.ANALYTICS,
      }),
    
    exportData: (exportData) =>
      api.post(API_CONFIG.ENDPOINTS.DIARY.EXPORT, exportData),
    
    // Fixed Questions Management
    getFixedQuestions: () =>
      api.get('/api/diary/fixed-questions'),
    
    updateFixedQuestions: (questions) =>
      api.put('/api/diary/fixed-questions', { questions }),
    
    regenerateSummary: (entryId) =>
      api.post(`/api/diary/regenerate-summary/${entryId}`),
    
    updateHappinessScore: (entryId, happiness_score) =>
      api.put(`/api/diary/entries/${entryId}/happiness-score`, { happiness_score }),
    
    updateResponse: (responseId, response_text) =>
      api.put(`/api/diary/responses/${responseId}`, { response_text }),
    
    // Visualization Charts (Phase 3)
    charts: {
      getHappinessTrend: (days = 30) =>
        api.get(`${API_CONFIG.ENDPOINTS.DIARY.CHARTS.HAPPINESS_TREND}?days=${days}`),
      
      getEmotionDistribution: (days = 30) =>
        api.get(`${API_CONFIG.ENDPOINTS.DIARY.CHARTS.EMOTION_DISTRIBUTION}?days=${days}`),
      
      getWeeklyPatterns: (weeks = 8) =>
        api.get(`${API_CONFIG.ENDPOINTS.DIARY.CHARTS.WEEKLY_PATTERNS}?weeks=${weeks}`),
      
      getRelationshipHealth: () =>
        api.get(API_CONFIG.ENDPOINTS.DIARY.CHARTS.RELATIONSHIP_HEALTH),
      
      getDashboard: () =>
        api.get(API_CONFIG.ENDPOINTS.DIARY.CHARTS.DASHBOARD),
      
      getMoodPrediction: (predictionData) =>
        api.post(API_CONFIG.ENDPOINTS.DIARY.CHARTS.MOOD_PREDICTION, predictionData),
    }
  },
  
  // Notifications and Push APIs removed

  // Relationships (Phase 3)
  relationships: {
    // Invitation Codes
    createInvitationCode: (codeData) =>
      api.post(API_CONFIG.ENDPOINTS.RELATIONSHIPS.CREATE_INVITATION_CODE, codeData),
    
    getInvitationCodes: (page = 1, pageSize = 20, activeOnly = true) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.GET_INVITATION_CODES}?page=${page}&page_size=${pageSize}&active_only=${activeOnly}`),
    
    useInvitationCode: (codeData) =>
      api.post(API_CONFIG.ENDPOINTS.RELATIONSHIPS.USE_INVITATION_CODE, codeData),
    
    // Legacy Email-based Requests
    sendRequest: (requestData) =>
      api.post(API_CONFIG.ENDPOINTS.RELATIONSHIPS.SEND_REQUEST, requestData),
    
    getReceivedRequests: (page = 1, pageSize = 20) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.REQUESTS_RECEIVED}?page=${page}&page_size=${pageSize}`),
    
    getSentRequests: (page = 1, pageSize = 20) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.REQUESTS_SENT}?page=${page}&page_size=${pageSize}`),
    
    respondToRequest: (requestId, responseData) =>
      api.post(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.RESPOND_REQUEST}/${requestId}/respond`, responseData),
    
    // Relationships Management
    getRelationships: (page = 1, pageSize = 20) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.LIST}?page=${page}&page_size=${pageSize}`),
    
    getRelationshipDetail: (relationshipId) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.DETAIL}/${relationshipId}`),
    
    getRelationshipInsights: (relationshipId, page = 1, pageSize = 10) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.INSIGHTS}/${relationshipId}/insights?page=${page}&page_size=${pageSize}`),
    
    getStats: () =>
      api.get(API_CONFIG.ENDPOINTS.RELATIONSHIPS.STATS),
    
    analyzeRelationship: (relationshipId, analysisData) =>
      api.post(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.ANALYZE}/${relationshipId}/analyze`, analysisData),
    
    getHealthReport: (relationshipId) =>
      api.get(`${API_CONFIG.ENDPOINTS.RELATIONSHIPS.HEALTH_REPORT}/${relationshipId}/health-report`),
  },

  // Voice methods
  voice: {
    getVoices: () =>
      api.get(API_CONFIG.ENDPOINTS.VOICE.VOICES),
    
    getStatus: () =>
      api.get(API_CONFIG.ENDPOINTS.VOICE.STATUS),
    
    transcribeAudio: (audioFile) => {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      return api.post(API_CONFIG.ENDPOINTS.VOICE.TRANSCRIBE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: TIMEOUT_CONFIG.VOICE,
      });
    },
    
    generateSpeech: (text, voice) => {
      const formData = new FormData();
      formData.append('text', text);
      if (voice) formData.append('voice', voice);
      return api.post(API_CONFIG.ENDPOINTS.VOICE.GENERATE_SPEECH, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    
    cleanup: () =>
      api.post(API_CONFIG.ENDPOINTS.VOICE.CLEANUP),
  },

  // Settings methods
  settings: {
    getOllamaModels: () =>
      api.get('/api/settings/ollama/models'),
    
    getOllamaStatus: () =>
      api.get('/api/settings/ollama/status'),
    
    setOllamaModel: (model) =>
      api.put('/api/settings/ollama/model', { model }),
    
    testOllamaModel: () =>
      api.get('/api/settings/ollama/test'),
  },
};

// Offline support utilities
export const offlineService = {
  // Save diary entry for offline sync
  saveDraftEntry: (entryData) => {
    const drafts = JSON.parse(localStorage.getItem(STORAGE_KEYS.OFFLINE_ENTRIES) || '[]');
    drafts.push({
      ...entryData,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      synced: false,
    });
    localStorage.setItem(STORAGE_KEYS.OFFLINE_ENTRIES, JSON.stringify(drafts));
  },

  // Get unsynced entries
  getUnsyncedEntries: () => {
    const drafts = JSON.parse(localStorage.getItem(STORAGE_KEYS.OFFLINE_ENTRIES) || '[]');
    return drafts.filter(entry => !entry.synced);
  },

  // Mark entry as synced
  markAsSynced: (entryId) => {
    const drafts = JSON.parse(localStorage.getItem(STORAGE_KEYS.OFFLINE_ENTRIES) || '[]');
    const updatedDrafts = drafts.map(entry =>
      entry.id === entryId ? { ...entry, synced: true } : entry
    );
    localStorage.setItem(STORAGE_KEYS.OFFLINE_ENTRIES, JSON.stringify(updatedDrafts));
  },

  // Sync offline entries when back online
  syncOfflineEntries: async () => {
    const unsyncedEntries = offlineService.getUnsyncedEntries();
    
    for (const entry of unsyncedEntries) {
      try {
        await apiService.diary.startSession(entry.sessionData);
        // Continue with response and completion...
        offlineService.markAsSynced(entry.id);
      } catch (error) {
        console.error('Failed to sync offline entry:', error);
      }
    }
  },
};

// Network status utilities
export const networkService = {
  isOnline: () => navigator.onLine,
  
  // Listen for online/offline events
  addNetworkListeners: (onOnline, onOffline) => {
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
  },
};

export { tokenManager };
export default api;
