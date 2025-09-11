import React, { useState } from 'react';
import { Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import Input from '../ui/Input';
import Button from '../ui/Button';
import { Card, CardContent } from '../ui/Card';

const MobileForm = ({
  fields = [],
  onSubmit,
  submitText = 'Submit',
  loading = false,
  error = '',
  className = '',
}) => {
  const [formData, setFormData] = useState({});
  const [showPasswords, setShowPasswords] = useState({});
  const [errors, setErrors] = useState({});

  const handleInputChange = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // Clear error when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => ({
        ...prev,
        [fieldName]: ''
      }));
    }
  };

  const validateField = (field) => {
    const value = formData[field.name] || '';
    
    if (field.required && !value.trim()) {
      return `${field.label} is required`;
    }
    
    if (field.minLength && value.length < field.minLength) {
      return `${field.label} must be at least ${field.minLength} characters`;
    }
    
    if (field.pattern && !field.pattern.test(value)) {
      return field.errorMessage || `${field.label} format is invalid`;
    }
    
    return '';
  };

  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    fields.forEach(field => {
      const error = validateField(field);
      if (error) {
        newErrors[field.name] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const togglePasswordVisibility = (fieldName) => {
    setShowPasswords(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const getFieldIcon = (field) => {
    if (field.type === 'password') {
      return showPasswords[field.name] ? 
        <EyeOff className="w-4 h-4" /> : 
        <Eye className="w-4 h-4" />;
    }
    return field.icon;
  };

  const getFieldType = (field) => {
    if (field.type === 'password' && showPasswords[field.name]) {
      return 'text';
    }
    return field.type;
  };

  return (
    <Card className={`w-full ${className}`}>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Form Fields */}
          {fields.map((field) => (
            <div key={field.name}>
              {field.type === 'select' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-error-500 ml-1">*</span>}
                  </label>
                  <select
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    className="input w-full"
                    required={field.required}
                    disabled={loading}
                  >
                    <option value="">{field.placeholder || `Select ${field.label}`}</option>
                    {field.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  {field.helperText && (
                    <p className="text-xs text-gray-500 mt-1">{field.helperText}</p>
                  )}
                </div>
              ) : field.type === 'textarea' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-error-500 ml-1">*</span>}
                  </label>
                  <textarea
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    placeholder={field.placeholder}
                    className="input w-full min-h-[100px] resize-none"
                    required={field.required}
                    disabled={loading}
                    rows={field.rows || 4}
                  />
                  {field.helperText && (
                    <p className="text-xs text-gray-500 mt-1">{field.helperText}</p>
                  )}
                </div>
              ) : (
                <Input
                  label={field.label}
                  type={getFieldType(field)}
                  name={field.name}
                  value={formData[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  leftIcon={field.icon}
                  rightIcon={field.type === 'password' ? (
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility(field.name)}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {getFieldIcon(field)}
                    </button>
                  ) : null}
                  error={errors[field.name]}
                  helperText={field.helperText}
                  required={field.required}
                  disabled={loading}
                />
              )}
            </div>
          ))}

          {/* Global Error */}
          {error && (
            <div className="bg-error-50 border border-error-200 rounded-lg p-4 animate-slide-up">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-error-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-error-800 font-medium">{error}</p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            disabled={loading}
            className="w-full h-14 text-base"
          >
            {submitText}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default MobileForm;
