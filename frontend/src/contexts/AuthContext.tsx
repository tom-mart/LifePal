'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setLoading(false);
      return;
    }

    setToken(accessToken);

    try {
      // Verify token by fetching user profile
      const profile = await apiClient.get<any>('/api/users/profile');
      setUser({
        id: profile.id,
        username: profile.user?.username || 'User',
        email: profile.user?.email || '',
      });
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.post<{
        access: string;
        refresh: string;
      }>('/api/token/pair', { username, password });

      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      setToken(response.access);

      // Fetch user profile
      await checkAuth();
      router.push('/chat');
    } catch (error: any) {
      throw new Error(error.message || 'Login failed');
    }
  };

  const register = async (username: string, password: string) => {
    try {
      await apiClient.post('/api/users/register', { username, password });
      // After registration, log in
      await login(username, password);
    } catch (error: any) {
      throw new Error(error.message || 'Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setToken(null);
    router.push('/');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
