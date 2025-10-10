import React, { useState } from 'react';
import { Key, Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import Modal from './ui/Modal';
import Button from './ui/Button';
import Input from './ui/Input';
import { Card, CardContent } from './ui/Card';

const ApiKeyModal = ({ isOpen, onClose, onSave }) => {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState('');
  const [isValid, setIsValid] = useState(false);

  // Load existing API key when modal opens, or use default key
  React.useEffect(() => {
    if (isOpen) {
      const existingKey = localStorage.getItem('groq_api_key');
      if (existingKey) {
        setApiKey(existingKey);
        validateApiKey(existingKey);
      } else {
        // Prefill with default API key from environment
        const defaultKey = import.meta.env.VITE_DEFAULT_GROQ_API_KEY || '';
        if (defaultKey) {
          setApiKey(defaultKey);
          validateApiKey(defaultKey);
        }
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
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add Groq API Key"
      size="md"
    >
      <div className="space-y-6">
        {/* Info Box */}
        <Card className="bg-primary-50 border-primary-200">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-primary-800 font-medium mb-1">Why do I need this?</p>
                <p className="text-primary-700 text-balance">
                  Your Groq API key is used to power the AI features like DPR updates, DLR analysis, and log insights. 
                  Your key is stored locally and never shared.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

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
              className={`input pl-10 pr-20 ${
                error ? 'input-error' : 
                isValid && apiKey ? 'input-success' : ''
              }`}
              disabled={isValidating}
            />
            <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
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
                  <CheckCircle className="w-4 h-4 text-success-600" />
                  <span className="text-sm text-success-600">Valid API key format</span>
                </>
              ) : error ? (
                <>
                  <AlertCircle className="w-4 h-4 text-error-600" />
                  <span className="text-sm text-error-600">{error}</span>
                </>
              ) : (
                <span className="text-sm text-gray-500">Enter your Groq API key</span>
              )}
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="text-sm text-gray-600">
          <p className="mb-2">Don't have a Groq API key?</p>
          <p>
            Get one free at{' '}
            <a 
              href="https://console.groq.com/keys" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 underline font-medium"
            >
              console.groq.com
            </a>
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            onClick={handleSkip}
            variant="secondary"
            size="md"
            className="flex-1"
            disabled={isValidating}
          >
            Close
          </Button>
          <Button
            type="button"
            onClick={handleSave}
            variant="primary"
            size="md"
            loading={isValidating}
            className="flex-1"
            disabled={!isValid || isValidating}
          >
            <Key className="w-4 h-4" />
            Save API Key
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default ApiKeyModal;
