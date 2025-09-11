import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';

// Simple test component to verify the app loads
function TestApp() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            AI Works Tracker - Test
          </h1>
          <p className="text-gray-600">
            If you can see this, the app is working!
          </p>
        </div>
      </div>
    </Router>
  );
}

export default TestApp;
