import React from 'react';
import { Link } from 'react-router-dom';

const RegisterPage = () => {
  return (
    <div className="min-h-screen bg-base-200 flex flex-col justify-center px-4 py-8">
      <div className="max-w-md mx-auto w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-4 mx-auto">
            <span className="text-2xl font-bold text-primary-content">L</span>
          </div>
          <h1 className="text-2xl font-bold text-base-content">Registration Disabled</h1>
          <p className="text-base-content/60 mt-2">New accounts are created by administrators only</p>
        </div>

        {/* Disabled message */}
        <div className="bg-base-100 rounded-2xl shadow-lg p-6">
          <div className="alert alert-info mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Registration Currently Disabled</h3>
              <div className="text-sm">New user accounts are created through the admin panel only.</div>
            </div>
          </div>

          <div className="space-y-4">
            <p className="text-base-content/80">
              To get access to LifePal, please contact an administrator who can create an account for you.
            </p>
            
            <div className="bg-base-200 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Need an account?</h4>
              <p className="text-sm text-base-content/70">
                If you're authorized to use LifePal, an administrator will provide you with login credentials.
              </p>
            </div>
          </div>

          {/* Login link */}
          <div className="text-center mt-6 pt-4 border-t border-base-300">
            <p className="text-sm text-base-content/60">
              Already have an account?{' '}
              <Link to="/auth/login" className="link link-primary font-medium">
                Sign In
              </Link>
            </p>
          </div>
        </div>

        {/* Back to home */}
        <div className="text-center mt-6">
          <Link to="/" className="btn btn-ghost btn-sm">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
