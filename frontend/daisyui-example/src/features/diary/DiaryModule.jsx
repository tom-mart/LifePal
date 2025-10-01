import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { DiaryProvider } from './context/DiaryContext.jsx';
import DiarySessionPage from './pages/DiarySessionPage.jsx';
import NewDiaryEntry from './pages/NewDiaryEntry.jsx';
import DiaryHistory from './pages/DiaryHistory.jsx';
import DiaryEntryDetail from './pages/DiaryEntryDetail.jsx';
import WellbeingCheck from './pages/WellbeingCheck.jsx';
import DiaryAnalyticsPage from './pages/DiaryAnalyticsPage.jsx';
import DiaryPredictionsPage from './pages/DiaryPredictionsPage.jsx';

const DiaryModule = () => {
  return (
    <DiaryProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/diary/session" replace />} />
        <Route path="/session" element={<DiarySessionPage />} />
        <Route path="/new" element={<NewDiaryEntry />} />
        <Route path="/history" element={<DiaryHistory />} />
        <Route path="/entries" element={<Navigate to="/diary/history" replace />} />
        <Route path="/entries/:id" element={<DiaryEntryDetail />} />
        <Route path="/wellbeing" element={<WellbeingCheck />} />
        <Route path="/analytics" element={<DiaryAnalyticsPage />} />
        <Route path="/predictions" element={<DiaryPredictionsPage />} />
        <Route path="*" element={<Navigate to="/diary/session" replace />} />
      </Routes>
    </DiaryProvider>
  );
};

export default DiaryModule;
