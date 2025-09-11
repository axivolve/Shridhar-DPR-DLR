import React, { forwardRef } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';

const Input = forwardRef(({
  label,
  error,
  success,
  helperText,
  leftIcon,
  rightIcon,
  className = '',
  ...props
}, ref) => {
  const inputClasses = [
    'input',
    error && 'input-error',
    success && 'input-success',
    leftIcon && 'pl-10',
    rightIcon && 'pr-10',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          className={inputClasses}
          {...props}
        />
        
        {/* Right Icon or Status Icons */}
        {error && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-error-500">
            <AlertCircle className="w-4 h-4" />
          </div>
        )}
        
        {success && !error && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-success-500">
            <CheckCircle className="w-4 h-4" />
          </div>
        )}
        
        {!error && !success && rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {rightIcon}
          </div>
        )}
      </div>
      
      {/* Helper Text */}
      {(error || helperText) && (
        <div className="mt-2">
          {error && (
            <p className="text-sm text-error-600 flex items-center gap-1">
              <AlertCircle className="w-4 h-4" />
              {error}
            </p>
          )}
          {helperText && !error && (
            <p className="text-sm text-gray-500">{helperText}</p>
          )}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
