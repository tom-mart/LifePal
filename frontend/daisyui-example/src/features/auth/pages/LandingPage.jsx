import React from 'react';
import { useNavigate } from 'react-router-dom';
import ThemeController from '../../../shared/components/ThemeController.jsx';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-secondary/5 to-accent/10">
      {/* Header with theme controller */}
      <header className="flex justify-end p-4">
        <ThemeController />
      </header>

      {/* Main content */}
      <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center">
        {/* Logo and branding */}
        <div className="mb-8">
          <div className="w-20 h-20 bg-primary rounded-2xl flex items-center justify-center mb-4 mx-auto shadow-lg">
            <span className="text-3xl font-bold text-primary-content">L</span>
          </div>
          <h1 className="text-4xl font-bold text-base-content mb-2">LifePal</h1>
          <p className="text-lg text-base-content/70 max-w-md">
            Your AI-powered life assistant for diary, wellness, and personal growth
          </p>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 max-w-2xl">
          <div className="bg-base-100/50 backdrop-blur-sm rounded-xl p-4 border border-base-300/50">
            <div className="text-2xl mb-2">📝</div>
            <h3 className="font-semibold text-sm mb-1">Smart Diary</h3>
            <p className="text-xs text-base-content/60">AI-powered questions that adapt to your patterns</p>
          </div>
          <div className="bg-base-100/50 backdrop-blur-sm rounded-xl p-4 border border-base-300/50">
            <div className="text-2xl mb-2">🎤</div>
            <h3 className="font-semibold text-sm mb-1">Voice Support</h3>
            <p className="text-xs text-base-content/60">Speak your thoughts with natural voice recording</p>
          </div>
          <div className="bg-base-100/50 backdrop-blur-sm rounded-xl p-4 border border-base-300/50">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-sm mb-1">Insights</h3>
            <p className="text-xs text-base-content/60">Track your wellbeing and emotional patterns</p>
          </div>
        </div>

        {/* CTA buttons */}
        <div className="space-y-3 w-full max-w-sm">
          <button 
            onClick={() => navigate('/auth/register')}
            className="btn btn-primary btn-lg w-full"
          >
            Get Started
          </button>
          <button 
            onClick={() => navigate('/auth/login')}
            className="btn btn-outline btn-lg w-full"
          >
            Sign In
          </button>
        </div>

        {/* PWA install hint */}
        <div className="browser-only mt-6 p-3 bg-info/10 rounded-lg border border-info/20 max-w-sm">
          <p className="text-xs text-info-content/80">
            💡 Add LifePal to your home screen for the best mobile experience
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center p-4 text-xs text-base-content/50">
        <p>© 2024 LifePal. Your privacy is our priority.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
