import React from 'react';
import { Plus } from 'lucide-react';

const FloatingActionButton = ({
  onClick,
  icon: Icon = Plus,
  label,
  position = 'bottom-right',
  size = 'md',
  className = '',
  ...props
}) => {
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  };

  const iconSizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-7 h-7',
  };

  return (
    <button
      onClick={onClick}
      className={`
        fixed z-40 bg-primary-600 hover:bg-primary-700 text-white
        rounded-full shadow-lg hover:shadow-xl
        transition-all duration-200 ease-in-out
        active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        ${positionClasses[position]}
        ${sizeClasses[size]}
        ${className}
      `}
      aria-label={label}
      {...props}
    >
      <Icon className={`${iconSizeClasses[size]} mx-auto`} />
    </button>
  );
};

export default FloatingActionButton;
