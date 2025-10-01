import React from 'react';
import FixedQuestionsManager from '../components/FixedQuestionsManager.jsx';

const QuestionsPage = () => {
  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-base-content mb-4">My Questions</h1>
          <p className="text-base-content/70 text-xl max-w-2xl mx-auto">
            Customize your 3 daily diary questions to make your reflection more meaningful
          </p>
        </div>

        {/* Fixed Questions Manager */}
        <FixedQuestionsManager />

        {/* Info Section */}
        <div className="bg-gradient-to-r from-primary/10 to-secondary/10 rounded-xl p-6 border border-primary/20">
          <h3 className="font-semibold text-primary-content mb-3">🌟 How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-primary-content/80">
            <div>
              <h4 className="font-medium mb-2">📝 Your 3 Fixed Questions</h4>
              <p>These are asked every day in your diary sessions. Make them personal and meaningful to you.</p>
            </div>
            <div>
              <h4 className="font-medium mb-2">🤖 + 2 AI Questions</h4>
              <p>Our AI adds 2 personalized questions based on your diary history and patterns.</p>
            </div>
          </div>
        </div>

        {/* Back Button */}
        <div className="text-center">
          <button
            onClick={() => window.history.back()}
            className="btn btn-ghost"
          >
            ← Back to Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionsPage;
