'use client';

import { useEffect, useState } from 'react';

export function ThemeDebug() {
  const [currentTheme, setCurrentTheme] = useState<string>('');

  useEffect(() => {
    const theme = document.documentElement.getAttribute('data-theme');
    setCurrentTheme(theme || 'none');
    
    // Watch for changes
    const observer = new MutationObserver(() => {
      const newTheme = document.documentElement.getAttribute('data-theme');
      setCurrentTheme(newTheme || 'none');
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
    
    return () => observer.disconnect();
  }, []);

  return (
    <div className="fixed bottom-4 right-4 bg-base-100 p-4 rounded-lg shadow-lg border border-base-300 z-50">
      <p className="text-sm">
        <strong>Current Theme:</strong> {currentTheme}
      </p>
      <p className="text-xs text-base-content/60 mt-1">
        DaisyUI Debug
      </p>
    </div>
  );
}
