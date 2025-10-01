import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext.jsx';
import LoadingSpinner from '../../shared/components/LoadingSpinner.jsx';
import ProtectedRoute from './ProtectedRoute.jsx';
import MobileLayout from './MobileLayout.jsx';

// Lazy load feature modules for code splitting
const AuthModule = lazy(() => import('../../features/auth/AuthModule.jsx'));
const DiaryModule = lazy(() => import('../../features/diary/DiaryModule.jsx'));
const DashboardModule = lazy(() => import('../../features/dashboard/DashboardModule.jsx'));
const RelationshipsPage = lazy(() => import('../../features/relationships/RelationshipsPage.jsx'));

// Landing page for unauthenticated users
const LandingPage = lazy(() => import('../../features/auth/pages/LandingPage.jsx'));

// 404 Not Found page
const NotFoundPage = () => (
  <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
    <h1 className="text-4xl font-bold text-primary mb-4">404</h1>
    <p className="text-lg text-base-content/70 mb-6">Page not found</p>
    <button 
      onClick={() => window.history.back()} 
      className="btn btn-primary"
    >
      Go Back
    </button>
  </div>
);

const AppRouter = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LandingPage />
              )
            } 
          />
          
          {/* Authentication routes */}
          <Route 
            path="/auth/*" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <AuthModule />
              )
            } 
          />

          {/* Protected routes with mobile layout */}
          <Route 
            path="/*" 
            element={
              <ProtectedRoute>
                <MobileLayout>
                  <Routes>
                    {/* Dashboard - main landing for authenticated users */}
                    <Route path="/dashboard/*" element={<DashboardModule />} />
                    
                    {/* Diary feature */}
                    <Route path="/diary/*" element={<DiaryModule />} />
                    
                    {/* Relationships feature (Phase 3) */}
                    <Route path="/relationships" element={<RelationshipsPage />} />
                    
                    {/* Future feature modules will be added here */}
                    {/* <Route path="/meals/*" element={<MealsModule />} /> */}
                    {/* <Route path="/shopping/*" element={<ShoppingModule />} /> */}
                    {/* <Route path="/finance/*" element={<FinanceModule />} /> */}
                    
                    {/* Default redirect to dashboard */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    
                    {/* 404 for protected routes */}
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </MobileLayout>
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default AppRouter;
