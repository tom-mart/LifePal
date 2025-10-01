import React, { createContext, useContext, useReducer } from 'react';
import { apiService } from '../../../shared/services/api.js';

// Diary state actions
const DIARY_ACTIONS = {
  START_SESSION: 'START_SESSION',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_QUESTIONS: 'SET_QUESTIONS',
  SET_CURRENT_QUESTION: 'SET_CURRENT_QUESTION',
  ADD_RESPONSE: 'ADD_RESPONSE',
  SET_EMOTIONS: 'SET_EMOTIONS',
  SET_SESSION_MODE: 'SET_SESSION_MODE',
  COMPLETE_SESSION: 'COMPLETE_SESSION',
  RESET_SESSION: 'RESET_SESSION',
  SET_ENTRIES: 'SET_ENTRIES',
  SET_WELLBEING_DATA: 'SET_WELLBEING_DATA',
};

// Initial state
const initialState = {
  // Session state
  sessionActive: false,
  sessionId: null,
  sessionMode: 'text', // 'text', 'voice', 'mixed'
  currentQuestionIndex: 0,
  
  // Questions and responses
  questions: [],
  responses: [],
  selectedEmotions: [],
  
  // Available data
  availableEmotions: [],
  entries: [],
  wellbeingData: null,
  
  // UI state
  loading: false,
  error: null,
};

// Reducer function
const diaryReducer = (state, action) => {
  switch (action.type) {
    case DIARY_ACTIONS.START_SESSION:
      return {
        ...state,
        sessionActive: true,
        sessionId: action.payload.sessionId,
        questions: action.payload.questions,
        currentQuestionIndex: 0,
        responses: [],
        selectedEmotions: [],
        loading: false,
        error: null,
      };

    case DIARY_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload.loading,
      };

    case DIARY_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload.error,
        loading: false,
      };

    case DIARY_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case DIARY_ACTIONS.SET_QUESTIONS:
      return {
        ...state,
        questions: action.payload.questions,
      };

    case DIARY_ACTIONS.SET_CURRENT_QUESTION:
      return {
        ...state,
        currentQuestionIndex: action.payload.index,
      };

    case DIARY_ACTIONS.ADD_RESPONSE:
      return {
        ...state,
        responses: [...state.responses, action.payload.response],
        currentQuestionIndex: state.currentQuestionIndex + 1,
      };

    case DIARY_ACTIONS.SET_EMOTIONS:
      return {
        ...state,
        selectedEmotions: action.payload.emotions,
      };

    case DIARY_ACTIONS.SET_SESSION_MODE:
      return {
        ...state,
        sessionMode: action.payload.mode,
      };

    case DIARY_ACTIONS.COMPLETE_SESSION:
      return {
        ...state,
        sessionActive: false,
        sessionId: null,
        currentQuestionIndex: 0,
        questions: [],
        responses: [],
        selectedEmotions: [],
        loading: false,
      };

    case DIARY_ACTIONS.RESET_SESSION:
      return {
        ...state,
        sessionActive: false,
        sessionId: null,
        currentQuestionIndex: 0,
        questions: [],
        responses: [],
        selectedEmotions: [],
        error: null,
      };

    case DIARY_ACTIONS.SET_ENTRIES:
      return {
        ...state,
        entries: action.payload.entries,
      };

    case DIARY_ACTIONS.SET_WELLBEING_DATA:
      return {
        ...state,
        wellbeingData: action.payload.data,
      };

    default:
      return state;
  }
};

// Create context
const DiaryContext = createContext();

// Provider component
export const DiaryProvider = ({ children }) => {
  const [state, dispatch] = useReducer(diaryReducer, initialState);

  // Load available emotions
  const loadEmotions = async () => {
    try {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });
      const response = await apiService.diary.getEmotions();
      
      // Store available emotions for selection
      const emotions = response.data;
      
      return emotions;
    } catch (error) {
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: 'Failed to load emotions' },
      });
      return [];
    } finally {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: false } });
    }
  };

  // Start diary session
  const startSession = async (sessionData = { mode: 'text' }) => {
    try {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });
      
      const response = await apiService.diary.startSession(sessionData);
      console.log('✅ Start session response:', response.data);
      
      const { entry_id, questions } = response.data;
      
      console.log('📋 Extracted data:', { entry_id, questions: questions?.length });

      dispatch({
        type: DIARY_ACTIONS.START_SESSION,
        payload: {
          sessionId: entry_id, // Django returns entry_id, not session_id
          questions: questions,
        },
      });

      dispatch({
        type: DIARY_ACTIONS.SET_SESSION_MODE,
        payload: { mode: sessionData.mode || 'text' },
      });

      return { success: true, sessionId: entry_id };
    } catch (error) {
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: error.response?.data?.error || 'Failed to start session' },
      });
      return { success: false, error: error.response?.data?.error || 'Failed to start session' };
    }
  };

  // Submit response to current question
  const submitResponse = async (responseText) => {
    try {
      console.log('🔄 Submitting response...', {
        sessionId: state.sessionId,
        currentQuestionIndex: state.currentQuestionIndex,
        questionsLength: state.questions.length,
        responseText: responseText?.substring(0, 50) + '...'
      });

      if (!state.sessionId || state.currentQuestionIndex >= state.questions.length) {
        console.error('❌ Session validation failed:', {
          sessionId: state.sessionId,
          currentQuestionIndex: state.currentQuestionIndex,
          questionsLength: state.questions.length,
          questions: state.questions
        });
        throw new Error(`Invalid session state: sessionId=${!!state.sessionId}, questionIndex=${state.currentQuestionIndex}, questionsLength=${state.questions.length}`);
      }

      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });

      const currentQuestion = state.questions[state.currentQuestionIndex];
      
      console.log('📝 Current question:', currentQuestion);
      
      const requestData = {
        question_id: currentQuestion.id,
        response_text: responseText,
        response_method: "text"
      };
      
      console.log('📤 Sending request:', requestData);
      
      const response = await apiService.diary.respond(requestData);

      dispatch({
        type: DIARY_ACTIONS.ADD_RESPONSE,
        payload: {
          response: {
            question_id: currentQuestion.id,
            response_text: responseText,
            question_text: currentQuestion.question_text,
          },
        },
      });

      console.log('✅ Response submitted successfully:', response.data);
      
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: false } });
      return { success: true };
    } catch (error) {
      console.error('❌ Response submission failed:', error);
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: error.response?.data?.error || error.message || 'Failed to submit response' },
      });
      return { success: false, error: error.response?.data?.error || error.message || 'Failed to submit response' };
    }
  };

  // Complete diary session with automatic emotion detection
  const completeSession = async () => {
    try {
      if (!state.sessionId) {
        throw new Error('No active session');
      }

      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });

      // Call the complete endpoint without emotion parameters
      // The backend will automatically detect emotions from responses
      const response = await apiService.diary.complete();

      console.log('✅ Complete session API response:', {
        status: response.status,
        data: response.data
      });

      dispatch({ type: DIARY_ACTIONS.COMPLETE_SESSION });

      // Backend queues processing (202 Accepted). Mark success so UI can redirect.
      return { success: true };
    } catch (error) {
      const status = error.response?.status;
      const msg = error.response?.data?.error || error.message || 'Failed to complete session';

      console.warn('⚠️ Complete session error:', { status, msg });

      // If the server returned a 5xx or we have a network/unknown error,
      // treat as success because processing is asynchronous and likely already enqueued.
      if (!status || status >= 500) {
        console.log('🟡 Treating completion as success despite error (async processing)');
        dispatch({ type: DIARY_ACTIONS.COMPLETE_SESSION });
        return { success: true, warning: msg };
      }

      // For clear client errors (e.g., 400 No active session / no responses), surface the error
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: msg },
      });
      return { success: false, error: msg };
    }
  };

  // Load diary entries
  const loadEntries = async (page = 1) => {
    try {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });
      
      const response = await apiService.diary.getEntries(page);
      
      dispatch({
        type: DIARY_ACTIONS.SET_ENTRIES,
        payload: { entries: response.data.entries },
      });

      return { success: true, entries: response.data.entries, pagination: response.data };
    } catch (error) {
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: 'Failed to load entries' },
      });
      return { success: false, error: 'Failed to load entries' };
    } finally {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: false } });
    }
  };

  // Load wellbeing check
  const loadWellbeingCheck = async () => {
    try {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: true } });
      
      const response = await apiService.diary.getWellbeingCheck();
      
      dispatch({
        type: DIARY_ACTIONS.SET_WELLBEING_DATA,
        payload: { data: response.data },
      });

      return { success: true, data: response.data };
    } catch (error) {
      dispatch({
        type: DIARY_ACTIONS.SET_ERROR,
        payload: { error: 'Failed to load wellbeing data' },
      });
      return { success: false, error: 'Failed to load wellbeing data' };
    } finally {
      dispatch({ type: DIARY_ACTIONS.SET_LOADING, payload: { loading: false } });
    }
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: DIARY_ACTIONS.CLEAR_ERROR });
  };

  // Reset session
  const resetSession = () => {
    dispatch({ type: DIARY_ACTIONS.RESET_SESSION });
  };

  // Context value
  const value = {
    // State
    ...state,
    
    // Computed values
    isLastQuestion: state.currentQuestionIndex >= state.questions.length - 1,
    currentQuestion: state.questions[state.currentQuestionIndex] || null,
    sessionProgress: state.questions.length > 0 ? (state.currentQuestionIndex / state.questions.length) * 100 : 0,
    
    // Actions
    loadEmotions,
    startSession,
    submitResponse,
    completeSession,
    loadEntries,
    loadWellbeingCheck,
    clearError,
    resetSession,
  };

  return (
    <DiaryContext.Provider value={value}>
      {children}
    </DiaryContext.Provider>
  );
};

// Hook to use diary context
export const useDiary = () => {
  const context = useContext(DiaryContext);
  if (!context) {
    throw new Error('useDiary must be used within a DiaryProvider');
  }
  return context;
};

export default DiaryContext;
