import React from 'react';
import logo from '../../assets/logo.png';

const Logo = ({ 
  size = 'md', 
  className = '', 
  showText = false,
  textClassName = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8', 
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl'
  };

  return (
    <div className={`flex items-center gap-2 ${className}`} {...props}>
      <img 
        src={logo} 
        alt="AI Works Tracker" 
        className={`${sizeClasses[size]} object-contain`}
      />
      {showText && (
        <span className={`font-semibold text-gray-900 ${textSizeClasses[size]} ${textClassName}`}>
          AI Works Tracker
        </span>
      )}
    </div>
  );
};

export default Logo;
