// API Configuration for LifePal
const getApiBaseUrl = () => {
  // Dynamic API URL based on current host
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  console.log('🌐 Current location:', { hostname, protocol, href: window.location.href });
  
  if (hostname === 'lifepal.app' || hostname.endsWith('.lifepal.app')) {
    // Domain access via Cloudflare tunnel - use same domain for API
    const apiUrl = `${protocol}//${hostname}`;
    console.log('🎯 Using same domain for API:', apiUrl);
    return apiUrl;
  } else if (hostname.startsWith('192.168.') || hostname.startsWith('10.') || hostname.startsWith('172.')) {
    // Local network access - use same protocol as current page
    const apiUrl = `${protocol}//${hostname}`;
    console.log('🏠 Using local network API URL:', apiUrl);
    return apiUrl;
  } else {
    // Default fallback
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    console.log('🔄 Using fallback API URL:', apiUrl);
    return apiUrl;
  }
};

const API_BASE_URL = getApiBaseUrl();
console.log('🔗 API Base URL:', API_BASE_URL, 'for hostname:', window.location.hostname);

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  ENDPOINTS: {
    // Authentication
    AUTH: {
      LOGIN: '/api/token/pair',
      REFRESH: '/api/token/refresh', 
      VERIFY: '/api/token/verify',
      REGISTER: '/api/users/register',
      PROFILE: '/api/users/profile',
      CHANGE_PASSWORD: '/api/users/change-password',
      STATS: '/api/users/stats',
    },
    
    // Diary
    DIARY: {
      START_SESSION: '/api/diary/start-session',
      RESPOND: '/api/diary/respond',
      COMPLETE: '/api/diary/complete',
      ENTRIES: '/api/diary/entries',
      ENTRY_DETAIL: '/api/diary/entries',
      WELLBEING_CHECK: '/api/diary/wellbeing-check',
      STATS: '/api/diary/stats',
      EMOTIONS: '/api/diary/emotions',
      QUESTION_INSIGHTS: '/api/diary/question-insights',
      
      // Advanced Analytics (Phase 3)
      PREDICT_MOOD: '/api/diary/predict-mood',
      RECOMMENDATIONS: '/api/diary/recommendations',
      EXPORT: '/api/diary/export',
      
      // Visualization Charts (Phase 3)
      CHARTS: {
        HAPPINESS_TREND: '/api/diary/charts/happiness-trend',
        EMOTION_DISTRIBUTION: '/api/diary/charts/emotion-distribution',
        WEEKLY_PATTERNS: '/api/diary/charts/weekly-patterns',
        RELATIONSHIP_HEALTH: '/api/diary/charts/relationship-health',
        DASHBOARD: '/api/diary/charts/dashboard',
        MOOD_PREDICTION: '/api/diary/charts/mood-prediction',
      }
    },
    
    // Relationships (Phase 3)
    RELATIONSHIPS: {
      // Invitation Codes
      CREATE_INVITATION_CODE: '/api/relationships/invitation-codes',
      GET_INVITATION_CODES: '/api/relationships/invitation-codes',
      USE_INVITATION_CODE: '/api/relationships/use-invitation-code',
      
      // Legacy Email-based Requests
      SEND_REQUEST: '/api/relationships/send-request',
      REQUESTS_RECEIVED: '/api/relationships/requests/received',
      REQUESTS_SENT: '/api/relationships/requests/sent',
      RESPOND_REQUEST: '/api/relationships/requests',
      
      // Relationships Management
      LIST: '/api/relationships/',
      DETAIL: '/api/relationships',
      INSIGHTS: '/api/relationships',
      STATS: '/api/relationships/stats',
      ANALYZE: '/api/relationships',
      HEALTH_REPORT: '/api/relationships',
    },
    
    // Voice
    VOICE: {
      VOICES: '/api/voice/voices',
      STATUS: '/api/voice/status',
      TRANSCRIBE: '/api/voice/transcribe',
      GENERATE_SPEECH: '/api/voice/generate-speech',
      CLEANUP: '/api/voice/cleanup',
    }
  }
};

// Request timeout configurations
export const TIMEOUT_CONFIG = {
  DEFAULT: 10000, // 10 seconds
  UPLOAD: 30000,  // 30 seconds for file uploads
  VOICE: 60000,   // 60 seconds for voice processing
  ANALYTICS: 60000, // 60 seconds for LLM/analytics endpoints
};

// Storage keys for local storage
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'lifepal_access_token',
  REFRESH_TOKEN: 'lifepal_refresh_token',
  USER_PROFILE: 'lifepal_user_profile',
  THEME: 'lifepal_theme',
  VOICE_PREFERENCE: 'lifepal_voice_preference',
  OFFLINE_ENTRIES: 'lifepal_offline_entries',
};

// Theme configuration
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark', 
  CUPCAKE: 'cupcake',
  EMERALD: 'emerald',
  CORPORATE: 'corporate',
  AUTUMN: 'autumn',
  SUNSET: 'sunset',
};

// Mobile breakpoints (matching Tailwind config)
export const BREAKPOINTS = {
  XS: 320,
  SM: 480,
  MD: 768,
  LG: 1024,
  XL: 1280,
};
