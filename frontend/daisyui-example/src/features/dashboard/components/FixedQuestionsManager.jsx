import React, { useState, useEffect } from 'react';
import { apiService } from '../../../shared/services/api.js';

const FixedQuestionsManager = () => {
  const [questions, setQuestions] = useState(['', '', '']);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  // Load user's current fixed questions
  useEffect(() => {
    loadFixedQuestions();
  }, []);

  const loadFixedQuestions = async () => {
    try {
      setLoading(true);
      const response = await apiService.diary.getFixedQuestions();
      
      if (response.data.questions && response.data.questions.length === 3) {
        const questionTexts = response.data.questions
          .sort((a, b) => a.order - b.order)
          .map(q => q.question_text);
        setQuestions(questionTexts);
      }
    } catch (error) {
      console.error('Failed to load fixed questions:', error);
      setError('Failed to load your questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionChange = (index, value) => {
    const newQuestions = [...questions];
    newQuestions[index] = value;
    setQuestions(newQuestions);
    setError('');
    setSaved(false);
  };

  const handleSave = async () => {
    // Validate questions
    for (let i = 0; i < questions.length; i++) {
      if (!questions[i].trim()) {
        setError(`Question ${i + 1} cannot be empty`);
        return;
      }
      if (questions[i].trim().length < 10) {
        setError(`Question ${i + 1} must be at least 10 characters long`);
        return;
      }
    }

    try {
      setSaving(true);
      setError('');
      
      await apiService.diary.updateFixedQuestions(questions.map(q => q.trim()));
      
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save fixed questions:', error);
      setError(error.response?.data?.error || 'Failed to save questions. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const resetToDefaults = () => {
    const defaultQuestions = [
      "How are you feeling today, and what's contributing to that feeling?",
      "What's one thing you're grateful for today, and why does it matter to you?",
      "What challenged you today, and how did you handle it?"
    ];
    setQuestions(defaultQuestions);
    setError('');
    setSaved(false);
  };

  if (loading) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="flex items-center justify-center py-8">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
            <span className="text-2xl">❓</span>
          </div>
          <div>
            <h2 className="card-title text-2xl">Fixed Questions</h2>
            <p className="text-base-content/60">Customize your 3 daily diary questions</p>
          </div>
        </div>

        {error && (
          <div className="alert alert-error mb-4">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
        )}

        {saved && (
          <div className="alert alert-success mb-4">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">Questions saved successfully!</span>
          </div>
        )}

        <div className="space-y-6">
          {questions.map((question, index) => (
            <div key={index}>
              <label className="label">
                <span className="label-text font-medium">Question {index + 1}</span>
                <span className="label-text-alt">{question.length}/200</span>
              </label>
              <textarea
                className="textarea textarea-bordered w-full h-24 resize-none"
                placeholder={`Enter your ${index + 1}${index === 0 ? 'st' : index === 1 ? 'nd' : 'rd'} daily question...`}
                value={question}
                onChange={(e) => handleQuestionChange(index, e.target.value)}
                maxLength={200}
              />
              <label className="label">
                <span className="label-text-alt text-xs">
                  This question will be asked every day in your diary sessions
                </span>
              </label>
            </div>
          ))}
        </div>

        <div className="card-actions justify-between mt-8">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={resetToDefaults}
            disabled={saving}
          >
            Reset to Defaults
          </button>
          
          <button
            type="button"
            className={`btn btn-primary w-auto px-8 ${saving ? 'loading' : ''} ${saved ? 'btn-success' : ''}`}
            onClick={handleSave}
            disabled={saving}
          >
            {saved ? '✅ Saved!' : saving ? 'Saving...' : 'Save Questions'}
          </button>
        </div>

        <div className="bg-info/10 rounded-xl p-4 mt-6">
          <h3 className="font-semibold text-info-content mb-2">💡 Tips for Great Questions</h3>
          <ul className="text-sm text-info-content/80 space-y-1">
            <li>• Make questions open-ended to encourage reflection</li>
            <li>• Focus on feelings, gratitude, and personal growth</li>
            <li>• Keep questions clear and easy to understand</li>
            <li>• Consider what insights would be most valuable to you</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FixedQuestionsManager;
