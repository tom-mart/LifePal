import React from 'react';
import { AuthProvider } from './core/auth/AuthContext.jsx';
import AppRouter from './core/navigation/AppRouter.jsx';
import PWAInstallPrompt from './core/pwa/PWAInstallPrompt.jsx';

function App() {
  return (
    <AuthProvider>
      <AppRouter />
      <PWAInstallPrompt />
    </AuthProvider>
  );
}

export default App;
