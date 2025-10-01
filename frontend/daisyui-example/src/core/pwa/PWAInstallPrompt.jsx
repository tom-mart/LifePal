import React, { useState, useEffect } from 'react';

const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      // Stash the event so it can be triggered later
      setDeferredPrompt(e);
      // Show our custom install prompt
      setShowPrompt(true);
    };

    const handleAppInstalled = () => {
      console.log('PWA was installed');
      setShowPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    // Show the install prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log(`User response to the install prompt: ${outcome}`);
    
    // Clear the deferredPrompt
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    // Remember user dismissed (optional - could use localStorage)
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  // Don't show if already dismissed or if running as PWA
  const isDismissed = localStorage.getItem('pwa-install-dismissed');
  const isPWA = window.matchMedia('(display-mode: standalone)').matches;

  if (!showPrompt || isDismissed || isPWA) {
    return null;
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-40 animate-slide-up">
      <div className="bg-primary text-primary-content rounded-xl p-4 shadow-lg border border-primary-focus">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-primary-content/20 rounded-lg flex items-center justify-center">
              <span className="text-lg">📱</span>
            </div>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-sm mb-1">Add LifePal to Home Screen</h3>
            <p className="text-xs opacity-90 mb-3">
              Install our app for the best mobile experience with offline diary writing
            </p>
            <div className="flex space-x-2">
              <button
                onClick={handleInstallClick}
                className="btn btn-sm btn-primary-content text-primary"
              >
                Install
              </button>
              <button
                onClick={handleDismiss}
                className="btn btn-sm btn-ghost text-primary-content/70"
              >
                Later
              </button>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 text-primary-content/70 hover:text-primary-content"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;
