import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardHome from './pages/DashboardHome.jsx';
import WellbeingDashboard from './pages/WellbeingDashboard.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';
import QuestionsPage from './pages/QuestionsPage.jsx';

const DashboardModule = () => {
  return (
    <Routes>
      <Route path="/" element={<DashboardHome />} />
      <Route path="/wellbeing" element={<WellbeingDashboard />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/questions" element={<QuestionsPage />} />
      <Route path="*" element={<Navigate to="/dashboard/" replace />} />
    </Routes>
  );
};

export default DashboardModule;
