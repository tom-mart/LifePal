import React, { useState, useEffect } from 'react';
import { THEMES, STORAGE_KEYS } from '../constants/api.js';

const ThemeController = () => {
  const [currentTheme, setCurrentTheme] = useState(THEMES.LIGHT);
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
    if (savedTheme && Object.values(THEMES).includes(savedTheme)) {
      setCurrentTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    }
  }, []);

  // Change theme
  const changeTheme = (theme) => {
    setCurrentTheme(theme);
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
    document.documentElement.setAttribute('data-theme', theme);
    setShowThemeMenu(false);
  };

  // Theme options with descriptions
  const themeOptions = [
    { 
      value: THEMES.LIGHT, 
      label: 'Light', 
      description: 'Clean and bright',
      icon: '☀️'
    },
    { 
      value: THEMES.DARK, 
      label: 'Dark', 
      description: 'Easy on the eyes',
      icon: '🌙'
    },
    { 
      value: THEMES.CUPCAKE, 
      label: 'Cupcake', 
      description: 'Soft and calming',
      icon: '🧁'
    },
    { 
      value: THEMES.EMERALD, 
      label: 'Emerald', 
      description: 'Fresh and natural',
      icon: '🌿'
    },
    { 
      value: THEMES.CORPORATE, 
      label: 'Corporate', 
      description: 'Professional look',
      icon: '💼'
    },
    { 
      value: THEMES.AUTUMN, 
      label: 'Autumn', 
      description: 'Warm and cozy',
      icon: '🍂'
    },
    { 
      value: THEMES.SUNSET, 
      label: 'Sunset', 
      description: 'Warm and reflective',
      icon: '🌅'
    },
  ];

  const getCurrentThemeOption = () => {
    return themeOptions.find(option => option.value === currentTheme) || themeOptions[0];
  };

  return (
    <div className="dropdown dropdown-end">
      <button 
        tabIndex={0} 
        className="btn btn-ghost btn-circle"
        onClick={() => setShowThemeMenu(!showThemeMenu)}
        title="Change theme"
      >
        <span className="text-lg">{getCurrentThemeOption().icon}</span>
      </button>
      
      {showThemeMenu && (
        <div className="dropdown-content z-50 mt-2 p-2 shadow-lg bg-base-100 rounded-box w-64 border border-base-300">
          <div className="p-2">
            <h3 className="font-semibold text-sm text-base-content mb-3">Choose Theme</h3>
            <div className="space-y-1">
              {themeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => changeTheme(option.value)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    currentTheme === option.value
                      ? 'bg-primary text-primary-content'
                      : 'hover:bg-base-200 text-base-content'
                  }`}
                >
                  <span className="text-lg">{option.icon}</span>
                  <div className="flex-1 text-left">
                    <div className="font-medium text-sm">{option.label}</div>
                    <div className={`text-xs ${
                      currentTheme === option.value 
                        ? 'text-primary-content/70' 
                        : 'text-base-content/60'
                    }`}>
                      {option.description}
                    </div>
                  </div>
                  {currentTheme === option.value && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThemeController;
