import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiService, tokenManager, networkService } from '../../shared/services/api.js';
import { STORAGE_KEYS } from '../../shared/constants/api.js';

// Auth action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  LOAD_USER: 'LOAD_USER',
  UPDATE_PROFILE: 'UPDATE_PROFILE',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Initial auth state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  isRegistering: false,
  isLoggingIn: false,
};

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoggingIn: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoggingIn: false,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoggingIn: false,
        isLoading: false,
        error: action.payload.error,
      };

    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        isRegistering: true,
        error: null,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isRegistering: false,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        isRegistering: false,
        error: action.payload.error,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false,
      };

    case AUTH_ACTIONS.LOAD_USER:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
      };

    case AUTH_ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        user: { ...state.user, ...action.payload.updates },
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload.loading,
      };

    case AUTH_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload.error,
        isLoading: false,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Create auth context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load user on app start
  useEffect(() => {
    loadUser();
  }, []);

  // Network status handling
  useEffect(() => {
    const cleanup = networkService.addNetworkListeners(
      () => {
        // When back online, try to sync any pending data
        console.log('Back online - syncing data...');
      },
      () => {
        console.log('Gone offline - enabling offline mode...');
      }
    );

    return cleanup;
  }, []);

  // Load user from stored token
  const loadUser = async () => {
    try {
      const token = tokenManager.getAccessToken();
      if (!token) {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: { loading: false } });
        return;
      }

      // Verify token and get user profile
      const profileResponse = await apiService.auth.getProfile();
      const user = profileResponse.data;

      // Store user profile
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.LOAD_USER,
        payload: { user },
      });
    } catch (error) {
      console.error('Failed to load user:', error);
      // Token is invalid, clear it
      tokenManager.clearTokens();
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: { loading: false } });
    }
  };

  // Login function
  const login = async (credentials) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });

      const response = await apiService.auth.login(credentials);
      const { access, refresh } = response.data;

      // Store tokens
      tokenManager.setTokens(access, refresh);
      
      // Get user profile after login
      const profileResponse = await apiService.auth.getProfile();
      const user = profileResponse.data;
      
      // Store user profile
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Login failed';
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: { error: errorMessage },
      });
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.REGISTER_START });

      // First, register the user
      const registerResponse = await apiService.auth.register(userData);
      
      // Registration successful, now log them in
      const loginResponse = await apiService.auth.login({
        email: userData.email,
        password: userData.password
      });
      
      const { access, refresh } = loginResponse.data;
      const user = registerResponse.data;

      // Store tokens
      tokenManager.setTokens(access, refresh);
      
      // Store user profile
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.REGISTER_SUCCESS,
        payload: { user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Registration failed';
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: { error: errorMessage },
      });
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = () => {
    tokenManager.clearTokens();
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  // Update profile function
  const updateProfile = async (updates) => {
    try {
      const response = await apiService.auth.updateProfile(updates);
      const updatedUser = response.data;

      // Update stored profile
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(updatedUser));

      dispatch({
        type: AUTH_ACTIONS.UPDATE_PROFILE,
        payload: { updates: updatedUser },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Profile update failed';
      dispatch({
        type: AUTH_ACTIONS.SET_ERROR,
        payload: { error: errorMessage },
      });
      return { success: false, error: errorMessage };
    }
  };

  // Change password function
  const changePassword = async (passwordData) => {
    try {
      await apiService.auth.changePassword(passwordData);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Password change failed';
      return { success: false, error: errorMessage };
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Context value
  const value = {
    // State
    ...state,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError,
    loadUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
