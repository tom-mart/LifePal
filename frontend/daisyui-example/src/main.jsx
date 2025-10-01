import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Balanced service worker management - no infinite loops
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {

      // Register service worker with no caching
      const registration = await navigator.serviceWorker.register('/sw.js', {
        updateViaCache: 'none'
      });
      
      console.log('✅ Service Worker registered:', registration);
      
      // Handle updates normally (no aggressive reloading)
      registration.addEventListener('updatefound', () => {
        console.log('🔄 Service Worker update found');
        const newWorker = registration.installing;
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('🆕 New Service Worker installed, will reload on next navigation');
            // Don't force immediate reload - let user navigate naturally
          }
        });
      });
      
      // Check for updates
      registration.update();
      
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
