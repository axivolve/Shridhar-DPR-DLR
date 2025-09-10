import React, { useState } from 'react';
import { Key, Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

const ApiKeyModal = ({ isOpen, onClose, onSave }) => {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState('');
  const [isValid, setIsValid] = useState(false);

  // Load existing API key when modal opens
  React.useEffect(() => {
    if (isOpen) {
      const existingKey = localStorage.getItem('groq_api_key');
      if (existingKey) {
        setApiKey(existingKey);
        validateApiKey(existingKey);
      }
    }
  }, [isOpen]);

  const validateApiKey = async (key) => {
    if (!key || key.length < 20) {
      setIsValid(false);
      return false;
    }

    // Basic validation - check if it starts with 'gsk_' (Groq API key format)
    if (!key.startsWith('gsk_')) {
      setError('Invalid Groq API key format. Keys should start with "gsk_"');
      setIsValid(false);
      return false;
    }

    setIsValid(true);
    setError('');
    return true;
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setApiKey(value);
    setError('');
    setIsValid(false);
    
    // Validate as user types
    if (value.length > 0) {
      validateApiKey(value);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setError('Please enter your Groq API key');
      return;
    }

    if (!isValid) {
      setError('Please enter a valid Groq API key');
      return;
    }

    setIsValidating(true);
    setError('');

    try {
      // Save to localStorage
      localStorage.setItem('groq_api_key', apiKey.trim());
      onSave(apiKey.trim());
      onClose();
    } catch (error) {
      setError('Failed to save API key. Please try again.');
    } finally {
      setIsValidating(false);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <Key className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Groq API Key
              </h2>
              <p className="text-sm text-gray-600">
                {localStorage.getItem('groq_api_key') ? 'Update your Groq API key' : 'Enter your Groq API key to use AI features'}
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-blue-800 font-medium mb-1">Why do I need this?</p>
                <p className="text-blue-700">
                  Your Groq API key is used to power the AI features like DPR updates, DLR analysis, and log insights. 
                  Your key is stored locally and never shared.
                </p>
              </div>
            </div>
          </div>

          {/* API Key Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Groq API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={handleInputChange}
                placeholder="gsk_..."
                className={`input-field pr-20 ${
                  error ? 'border-red-300 focus:ring-red-500' : 
                  isValid ? 'border-green-300 focus:ring-green-500' : ''
                }`}
                disabled={isValidating}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isValidating}
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            
            {/* Validation Status */}
            {apiKey && (
              <div className="mt-2 flex items-center gap-2">
                {isValid ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-600">Valid API key format</span>
                  </>
                ) : error ? (
                  <>
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-sm text-red-600">{error}</span>
                  </>
                ) : (
                  <span className="text-sm text-gray-500">Enter your Groq API key</span>
                )}
              </div>
            )}
          </div>

          {/* Help Text */}
          <div className="text-xs text-gray-500">
            <p className="mb-1">Don't have a Groq API key?</p>
            <p>
              Get one free at{' '}
              <a 
                href="https://console.groq.com/keys" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 underline"
              >
                console.groq.com
              </a>
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={handleSkip}
            className="flex-1 btn-secondary"
            disabled={isValidating}
          >
            Close
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="flex-1 btn-primary flex items-center justify-center gap-2"
            disabled={!isValid || isValidating}
          >
            {isValidating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Key className="w-4 h-4" />
                Save API Key
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyModal;
