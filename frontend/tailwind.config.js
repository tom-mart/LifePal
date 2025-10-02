/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Mobile-first breakpoints
      screens: {
        'xs': '320px',
        'sm': '480px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
      },
      // Safe area insets for mobile devices
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      // Touch-friendly sizes
      minHeight: {
        'touch': '44px', // Minimum touch target size
      },
      minWidth: {
        'touch': '44px',
      },
    },
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      // LifePal custom themes
      {
        lifepal: {
          "primary": "#4f46e5",          // Indigo
          "primary-focus": "#4338ca",    // Darker indigo
          "primary-content": "#ffffff",  // White text on primary
          "secondary": "#06b6d4",        // Cyan
          "secondary-focus": "#0891b2",  // Darker cyan
          "secondary-content": "#ffffff",// White text on secondary
          "accent": "#8b5cf6",           // Violet
          "neutral": "#1f2937",          // Dark gray
          "base-100": "#ffffff",         // White background
          "base-200": "#f3f4f6",         // Very light gray
          "base-300": "#e5e7eb",         // Light gray border
          "info": "#3b82f6",             // Blue
          "success": "#10b981",          // Green
          "warning": "#f59e0b",          // Amber
          "error": "#ef4444"             // Red
        },
      },
      {
        "lifepal-dark": {
          "primary": "#818cf8",          // Lighter indigo
          "primary-focus": "#6366f1",    // Mid indigo
          "primary-content": "#1e293b",  // Dark text on primary
          "secondary": "#22d3ee",        // Lighter cyan
          "secondary-focus": "#06b6d4",  // Mid cyan
          "secondary-content": "#1e293b",// Dark text on secondary
          "accent": "#a78bfa",           // Lighter violet
          "neutral": "#f3f4f6",          // Light neutral
          "base-100": "#1e293b",         // Dark background
          "base-200": "#334155",         // Medium dark
          "base-300": "#475569",         // Lighter dark
          "info": "#60a5fa",             // Lighter blue
          "success": "#34d399",          // Lighter green
          "warning": "#fbbf24",          // Lighter amber
          "error": "#f87171"             // Lighter red
        },
      },
      // Standard themes
      "light",
      "dark",
      "cupcake",
      "emerald",
      "corporate",
      "autumn",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "winter",
      "dim",
      "nord",
      "sunset",
    ],
    darkTheme: "lifepal-dark",
    base: true,
    styled: true,
    utils: true,
    prefix: "",
    logs: true,
    themeRoot: ":root",
  },
};
