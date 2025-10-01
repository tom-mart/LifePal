import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../core/auth/AuthContext.jsx';
import { apiService } from '../../../shared/services/api.js';

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuth();
  
  // Settings state
  const [questions, setQuestions] = useState(['', '', '']);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  // Loading states
  const [questionsLoading, setQuestionsLoading] = useState(true);
  const [voicesLoading, setVoicesLoading] = useState(true);
  const [modelsLoading, setModelsLoading] = useState(true);
  
  // Saving states
  const [questionsSaving, setQuestionsSaving] = useState(false);
  const [voiceSaving, setVoiceSaving] = useState(false);
  const [modelSaving, setModelSaving] = useState(false);
  const [modelTesting, setModelTesting] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  
  // Success states
  const [questionsSaved, setQuestionsSaved] = useState(false);
  const [voiceSaved, setVoiceSaved] = useState(false);
  const [modelSaved, setModelSaved] = useState(false);
  const [modelTested, setModelTested] = useState(false);
  const [passwordSaved, setPasswordSaved] = useState(false);
  
  // Error states
  const [questionsError, setQuestionsError] = useState('');
  const [voiceError, setVoiceError] = useState('');
  const [modelError, setModelError] = useState('');
  const [modelTestError, setModelTestError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  useEffect(() => {
    if (user) {
      setSelectedVoice(user.preferred_voice || 'en-US-AriaNeural');
      loadFixedQuestions();
      loadAvailableVoices();
      loadAvailableModels();
    }
  }, [user]);

  const loadFixedQuestions = async () => {
    try {
      setQuestionsLoading(true);
      const response = await apiService.diary.getFixedQuestions();
      
      console.log('Fixed questions response:', response.data);
      
      if (response.data.questions && response.data.questions.length === 3) {
        const questionTexts = response.data.questions
          .sort((a, b) => a.order - b.order)
          .map(q => q.question_text);
        setQuestions(questionTexts);
      } else {
        // Fallback to default questions if API doesn't return 3 questions
        const defaultQuestions = [
          "How are you feeling today, and what's contributing to that feeling?",
          "What's one thing you're grateful for today, and why does it matter to you?",
          "What challenged you today, and how did you handle it?"
        ];
        setQuestions(defaultQuestions);
      }
    } catch (error) {
      console.error('Failed to load fixed questions:', error);
      // Set default questions on error
      const defaultQuestions = [
        "How are you feeling today, and what's contributing to that feeling?",
        "What's one thing you're grateful for today, and why does it matter to you?",
        "What challenged you today, and how did you handle it?"
      ];
      setQuestions(defaultQuestions);
      setQuestionsError('Loaded default questions. You can customize them below.');
    } finally {
      setQuestionsLoading(false);
    }
  };

  const loadAvailableVoices = async () => {
    try {
      setVoicesLoading(true);
      const response = await apiService.voice.getVoices();
      setAvailableVoices(response.data || []);
    } catch (error) {
      console.error('Failed to load voices:', error);
      setVoiceError('Failed to load available voices');
    } finally {
      setVoicesLoading(false);
    }
  };

  const loadAvailableModels = async () => {
    try {
      setModelsLoading(true);
      
      // Get available models and current status
      const [modelsResponse, statusResponse] = await Promise.all([
        apiService.settings.getOllamaModels(),
        apiService.settings.getOllamaStatus()
      ]);
      
      setAvailableModels(modelsResponse.data || []);
      setSelectedModel(statusResponse.data.current_model || 'gemma2:latest');
      
    } catch (error) {
      console.error('Failed to load models:', error);
      setModelError('Failed to load available models. Please check if Ollama server is running.');
      
      // Fallback to mock data if API fails
      const fallbackModels = [
        { name: 'gemma2:latest', size: 'Unknown' },
        { name: 'llama3.1:latest', size: 'Unknown' },
        { name: 'mistral:latest', size: 'Unknown' },
      ];
      setAvailableModels(fallbackModels);
      setSelectedModel(user?.preferred_ollama_model || 'gemma2:latest');
    } finally {
      setModelsLoading(false);
    }
  };

  const handleSaveVoice = async () => {
    try {
      setVoiceSaving(true);
      setVoiceError('');
      
      await apiService.auth.updateProfile({ preferred_voice: selectedVoice });
      
      setVoiceSaved(true);
      setTimeout(() => setVoiceSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save voice preference:', error);
      setVoiceError('Failed to save voice preference. Please try again.');
    } finally {
      setVoiceSaving(false);
    }
  };

  const handleSaveModel = async () => {
    try {
      setModelSaving(true);
      setModelError('');
      
      // Save model preference via API
      await apiService.settings.setOllamaModel(selectedModel);
      
      // Update user profile to reflect the change
      if (updateUser) {
        updateUser({ ...user, preferred_ollama_model: selectedModel });
      }
      
      setModelSaved(true);
      setTimeout(() => setModelSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save model preference:', error);
      setModelError(error.response?.data?.error || 'Failed to save model preference. Please try again.');
    } finally {
      setModelSaving(false);
    }
  };

  const handleTestModel = async () => {
    try {
      setModelTesting(true);
      setModelTestError('');
      
      // Test the current model
      const response = await apiService.settings.testOllamaModel();
      
      console.log('Model test response:', response.data);
      setModelTested(true);
      setTimeout(() => setModelTested(false), 5000);
    } catch (error) {
      console.error('Failed to test model:', error);
      setModelTestError(error.response?.data?.error || 'Failed to test model. Please check if Ollama server is running.');
    } finally {
      setModelTesting(false);
    }
  };

  const handleChangePassword = async () => {
    try {
      setPasswordSaving(true);
      setPasswordError('');
      
      if (passwordData.new_password !== passwordData.confirm_password) {
        setPasswordError('New passwords do not match');
        return;
      }
      
      if (passwordData.new_password.length < 8) {
        setPasswordError('New password must be at least 8 characters long');
        return;
      }
      
      await apiService.auth.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setPasswordSaved(true);
      setTimeout(() => setPasswordSaved(false), 3000);
    } catch (error) {
      console.error('Failed to change password:', error);
      setPasswordError(error.response?.data?.error || 'Failed to change password. Please try again.');
    } finally {
      setPasswordSaving(false);
    }
  };

  const handlePasswordChange = (field, value) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
    setPasswordError('');
    setPasswordSaved(false);
  };

  const handleQuestionChange = (index, value) => {
    const newQuestions = [...questions];
    newQuestions[index] = value;
    setQuestions(newQuestions);
    setQuestionsError('');
    setQuestionsSaved(false);
  };

  const handleSaveQuestions = async () => {
    // Validate questions
    for (let i = 0; i < questions.length; i++) {
      if (!questions[i].trim()) {
        setQuestionsError(`Question ${i + 1} cannot be empty`);
        return;
      }
      if (questions[i].trim().length < 10) {
        setQuestionsError(`Question ${i + 1} must be at least 10 characters long`);
        return;
      }
    }

    try {
      setQuestionsSaving(true);
      setQuestionsError('');
      
      await apiService.diary.updateFixedQuestions(questions.map(q => q.trim()));
      
      setQuestionsSaved(true);
      setTimeout(() => setQuestionsSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save fixed questions:', error);
      setQuestionsError(error.response?.data?.error || 'Failed to save questions. Please try again.');
    } finally {
      setQuestionsSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="p-4">
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Breadcrumb */}
        <div className="breadcrumbs text-sm">
          <ul>
            <li><a onClick={() => navigate('/dashboard')} className="cursor-pointer">Dashboard</a></li>
            <li>Settings</li>
          </ul>
        </div>
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-base-content mb-2">Settings</h1>
          <p className="text-base-content/60">Configure your LifePal experience</p>
        </div>

        {/* Notifications removed */}

        {/* Ollama Model Selection */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🤖</span>
              </div>
              <div>
                <h2 className="card-title text-2xl">AI Model Selection</h2>
                <p className="text-base-content/60">Choose the Ollama model for diary processing</p>
              </div>
            </div>

            {modelError && (
              <div className="alert alert-error mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{modelError}</span>
              </div>
            )}

            {modelSaved && (
              <div className="alert alert-success mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Model preference saved successfully!</span>
              </div>
            )}

            {modelTested && (
              <div className="alert alert-success mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Model test completed successfully!</span>
              </div>
            )}

            {modelTestError && (
              <div className="alert alert-warning mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{modelTestError}</span>
              </div>
            )}

            {modelsLoading ? (
              <div className="flex items-center justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="label">
                    <span className="label-text font-medium">Available Models</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {availableModels.map(model => (
                      <option key={model.name} value={model.name}>
                        {model.name} {model.size && model.size !== 'Unknown' ? `(${model.size})` : ''}
                      </option>
                    ))}
                  </select>
                  <label className="label">
                    <span className="label-text-alt">Different models have varying capabilities and resource requirements</span>
                  </label>
                </div>

                <div className="card-actions justify-end mt-6 gap-3">
                  <button
                    className={`btn btn-outline ${modelTesting ? 'loading' : ''} ${modelTested ? 'btn-success' : ''}`}
                    onClick={handleTestModel}
                    disabled={modelTesting || modelSaving}
                  >
                    {modelTested ? '✅ Test Passed!' : modelTesting ? 'Testing...' : '🧪 Test Model'}
                  </button>
                  <button
                    className={`btn btn-secondary ${modelSaving ? 'loading' : ''} ${modelSaved ? 'btn-success' : ''}`}
                    onClick={handleSaveModel}
                    disabled={modelSaving || modelTesting}
                  >
                    {modelSaved ? '✅ Saved!' : modelSaving ? 'Saving...' : 'Save Model'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Voice Settings */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🎤</span>
              </div>
              <div>
                <h2 className="card-title text-2xl">Voice Settings</h2>
                <p className="text-base-content/60">Configure text-to-speech voice for diary questions</p>
              </div>
            </div>

            {voiceError && (
              <div className="alert alert-error mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{voiceError}</span>
              </div>
            )}

            {voiceSaved && (
              <div className="alert alert-success mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Voice preference saved successfully!</span>
              </div>
            )}

            {voicesLoading ? (
              <div className="flex items-center justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="label">
                    <span className="label-text font-medium">Available Voices</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={selectedVoice}
                    onChange={(e) => setSelectedVoice(e.target.value)}
                  >
                    {availableVoices.length > 0 ? (
                      availableVoices.map(voice => (
                        <option key={voice.name} value={voice.name}>
                          {voice.display_name || voice.name} ({voice.gender}, {voice.locale})
                        </option>
                      ))
                    ) : (
                      <option value="en-US-AriaNeural">en-US-AriaNeural (Female, en-US)</option>
                    )}
                  </select>
                  <label className="label">
                    <span className="label-text-alt">Choose a voice that feels comfortable for your diary sessions</span>
                  </label>
                </div>

                <div className="card-actions justify-end mt-6">
                  <button
                    className={`btn btn-accent ${voiceSaving ? 'loading' : ''} ${voiceSaved ? 'btn-success' : ''}`}
                    onClick={handleSaveVoice}
                    disabled={voiceSaving}
                  >
                    {voiceSaved ? '✅ Saved!' : voiceSaving ? 'Saving...' : 'Save Voice'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Fixed Questions Management */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                <span className="text-2xl">❓</span>
              </div>
              <div>
                <h2 className="card-title text-2xl">Daily Questions</h2>
                <p className="text-base-content/60">Customize your 3 fixed diary questions</p>
              </div>
            </div>

            {questionsError && (
              <div className="alert alert-error mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{questionsError}</span>
              </div>
            )}

            {questionsSaved && (
              <div className="alert alert-success mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Questions saved successfully!</span>
              </div>
            )}

            {questionsLoading ? (
              <div className="flex items-center justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : (
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
                  </div>
                ))}

                <div className="card-actions justify-end mt-6">
                  <button
                    type="button"
                    className={`btn btn-primary w-auto px-8 ${questionsSaving ? 'loading' : ''} ${questionsSaved ? 'btn-success' : ''}`}
                    onClick={handleSaveQuestions}
                    disabled={questionsSaving}
                  >
                    {questionsSaved ? '✅ Saved!' : questionsSaving ? 'Saving...' : 'Save Questions'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Password Change */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-error/10 rounded-xl flex items-center justify-center">
                <span className="text-2xl">🔒</span>
              </div>
              <div>
                <h2 className="card-title text-2xl">Security</h2>
                <p className="text-base-content/60">Change your account password</p>
              </div>
            </div>

            {passwordError && (
              <div className="alert alert-error mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{passwordError}</span>
              </div>
            )}

            {passwordSaved && (
              <div className="alert alert-success mb-4">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Password changed successfully!</span>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="label">
                  <span className="label-text font-medium">Current Password</span>
                </label>
                <input
                  type="password"
                  className="input input-bordered w-full"
                  value={passwordData.current_password}
                  onChange={(e) => handlePasswordChange('current_password', e.target.value)}
                  placeholder="Enter current password"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text font-medium">New Password</span>
                </label>
                <input
                  type="password"
                  className="input input-bordered w-full"
                  value={passwordData.new_password}
                  onChange={(e) => handlePasswordChange('new_password', e.target.value)}
                  placeholder="Enter new password (min 8 characters)"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text font-medium">Confirm New Password</span>
                </label>
                <input
                  type="password"
                  className="input input-bordered w-full"
                  value={passwordData.confirm_password}
                  onChange={(e) => handlePasswordChange('confirm_password', e.target.value)}
                  placeholder="Confirm new password"
                />
              </div>
            </div>
            
            <div className="card-actions justify-end mt-6">
              <button 
                className={`btn btn-error ${passwordSaving ? 'loading' : ''} ${passwordSaved ? 'btn-success' : ''}`}
                onClick={handleChangePassword}
                disabled={passwordSaving}
              >
                {passwordSaved ? '✅ Changed!' : passwordSaving ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-4">
          <button
            onClick={() => window.history.back()}
            className="btn btn-ghost"
          >
            ← Back to Dashboard
          </button>
          <button
            onClick={() => window.location.href = '/dashboard/profile'}
            className="btn btn-secondary"
          >
            👤 View Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
