import React, { useState } from 'react';
import { User, AtSign, CheckCircle } from 'lucide-react';
import { authAPI } from '../api';

const ProfileCompletionForm = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    name: '',
    username: ''
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      onError('Please enter your name');
      return false;
    }

    if (!formData.username.trim()) {
      onError('Please enter a username');
      return false;
    }

    // Validate username (alphanumeric and underscores only)
    if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      onError('Username can only contain letters, numbers, and underscores');
      return false;
    }

    if (formData.username.length < 3) {
      onError('Username must be at least 3 characters long');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.completeProfile(formData);

      if (response.data.success) {
        // Update token
        localStorage.setItem('jwt_token', response.data.token);
        
        onSuccess(response.data);
      } else {
        onError(response.data.message || 'Profile completion failed');
      }
    } catch (error) {
      console.error('Profile completion error:', error);
      onError(error.response?.data?.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="card">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Complete Your Profile
          </h1>
          <p className="text-gray-600">
            Just a few more details to personalize your experience
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                className="input pl-10"
                required
              />
            </div>
          </div>

          {/* Username */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <AtSign className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Choose a username"
                className="input pl-10"
                required
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Username can contain letters, numbers, and underscores (min 3 characters)
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Completing Profile...
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                Complete Profile
              </>
            )}
          </button>
        </form>

        {/* Info */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Next step:</strong> After completing your profile, you'll be redirected to Google login to connect your Google account for accessing Google Sheets.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfileCompletionForm;
