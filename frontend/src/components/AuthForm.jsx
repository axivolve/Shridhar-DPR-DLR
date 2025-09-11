import React, { useState } from 'react';
import { Phone, Lock, User, AtSign, ArrowLeft } from 'lucide-react';
import { authAPI } from '../api';
import Button from './ui/Button';
import Input from './ui/Input';
import { Card, CardContent } from './ui/Card';
import MobileForm from './forms/MobileForm';

const AuthForm = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    mobile_number: '',
    password: '',
    name: '',
    username: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showSignupFields, setShowSignupFields] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (error) setError('');
  };

  const validateForm = () => {
    if (!formData.mobile_number || !formData.password) {
      setError('Mobile number and password are required');
      return false;
    }

    if (showSignupFields) {
      if (!formData.name || !formData.username) {
        setError('Name and username are required for signup');
        return false;
      }
      if (formData.name.length < 2) {
        setError('Name must be at least 2 characters');
        return false;
      }
      if (formData.username.length < 3) {
        setError('Username must be at least 3 characters');
        return false;
      }
    }

    return true;
  };

  const handleFormSubmit = async (formData) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await authAPI.authenticate(formData);
      const data = response.data;

      if (data.success) {
        // Store user data and token
        localStorage.setItem('jwt_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Call success callback
        onSuccess(data);
      } else {
        if (data.error === 'user_not_found' && !showSignupFields) {
          // User doesn't exist, show signup fields
          setShowSignupFields(true);
          setError('User not found. Please provide your details to sign up.');
        } else {
          setError(data.message || 'Authentication failed');
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setError(error.response?.data?.message || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToLogin = () => {
    setShowSignupFields(false);
    setFormData(prev => ({
      mobile_number: prev.mobile_number,
      password: prev.password,
      name: '',
      username: ''
    }));
    setError('');
  };

  // Define form fields based on current state
  const getFormFields = () => {
    const baseFields = [
      {
        name: 'mobile_number',
        label: 'Mobile Number',
        type: 'tel',
        placeholder: 'Enter your mobile number',
        icon: <Phone className="w-4 h-4" />,
        required: true,
        pattern: /^[0-9+\-\s()]+$/,
        errorMessage: 'Please enter a valid mobile number'
      },
      {
        name: 'password',
        label: 'Password',
        type: 'password',
        placeholder: 'Enter your password',
        icon: <Lock className="w-4 h-4" />,
        required: true,
        minLength: 6,
        errorMessage: 'Password must be at least 6 characters'
      }
    ];

    if (showSignupFields) {
      baseFields.push(
        {
          name: 'name',
          label: 'Full Name',
          type: 'text',
          placeholder: 'Enter your full name',
          icon: <User className="w-4 h-4" />,
          required: true,
          minLength: 2,
          errorMessage: 'Name must be at least 2 characters'
        },
        {
          name: 'username',
          label: 'Username',
          type: 'text',
          placeholder: 'Choose a username',
          icon: <AtSign className="w-4 h-4" />,
          required: true,
          minLength: 3,
          pattern: /^[a-zA-Z0-9_]+$/,
          errorMessage: 'Username can only contain letters, numbers, and underscores',
          helperText: 'Username can contain letters, numbers, and underscores (min 3 characters)'
        }
      );
    }

    return baseFields;
  };

  return (
    <div className="w-full">
      <div className="text-center mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
          {showSignupFields ? 'Create Account' : 'Welcome Back'}
        </h1>
        <p className="text-gray-600 text-balance">
          {showSignupFields 
            ? 'Enter your details to create a new account' 
            : 'Sign in to your account to continue'
          }
        </p>
      </div>

      <MobileForm
        fields={getFormFields()}
        onSubmit={handleFormSubmit}
        submitText={showSignupFields ? 'Create Account' : 'Sign In'}
        loading={isLoading}
        error={error}
      />

      {/* Back to Login Link */}
      {showSignupFields && (
        <div className="text-center mt-4">
          <Button
            type="button"
            onClick={handleBackToLogin}
            variant="ghost"
            size="md"
            disabled={isLoading}
            className="w-full"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Sign In
          </Button>
        </div>
      )}
    </div>
  );
};

export default AuthForm;