import React from 'react';

const NewDiaryEntry = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">New Diary Entry</h1>
      <div className="bg-base-100 rounded-xl p-6 border border-base-300">
        <p className="text-center text-base-content/60 mb-4">
          Ready to connect with your sophisticated AI diary system?
        </p>
        <div className="space-y-2 text-sm text-base-content/70">
          <p>✨ Advanced dynamic questions based on your patterns</p>
          <p>🎤 Voice recording with natural TTS</p>
          <p>📊 Happiness scoring and wellbeing analysis</p>
          <p>🔒 Encrypted storage for privacy</p>
        </div>
        <div className="mt-6 text-center">
          <button className="btn btn-primary">Start Diary Session</button>
        </div>
      </div>
    </div>
  );
};

export default NewDiaryEntry;
