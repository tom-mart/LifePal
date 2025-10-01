import React from 'react';

const LoadingSpinner = ({ size = 'md', message = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'loading-sm',
    md: 'loading-md', 
    lg: 'loading-lg',
    xl: 'loading-lg', // DaisyUI doesn't have xl, use lg
  };

  return (
    <div className="mobile-loading">
      <div className="flex flex-col items-center space-y-4">
        <span className={`loading loading-spinner text-primary ${sizeClasses[size]}`}></span>
        {message && (
          <p className="text-base-content/70 text-sm font-medium animate-pulse">
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;
