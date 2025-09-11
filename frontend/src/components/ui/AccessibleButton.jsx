import React from 'react';
import { useAriaAttributes } from '../../hooks/useAccessibility';

const AccessibleButton = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  onClick,
  onKeyDown,
  ariaLabel,
  ariaDescribedBy,
  ...props
}) => {
  const { ariaProps, otherProps } = useAriaAttributes({
    role: 'button',
    ariaLabel: ariaLabel || (typeof children === 'string' ? children : undefined),
    ariaDescribedBy,
    ariaDisabled: disabled || loading,
    ...props
  });

  const baseClasses = 'btn';
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    outline: 'btn-outline',
    ghost: 'btn-ghost',
    danger: 'btn-danger',
    success: 'btn-success',
  };
  const sizeClasses = {
    sm: 'btn-sm',
    md: 'btn-md',
    lg: 'btn-lg',
    xl: 'btn-xl',
  };

  const classes = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className
  ].filter(Boolean).join(' ');

  const handleKeyDown = (e) => {
    // Handle Enter and Space keys
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled && !loading && onClick) {
        onClick(e);
      }
    }
    
    if (onKeyDown) {
      onKeyDown(e);
    }
  };

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      {...ariaProps}
      {...otherProps}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
};

export default AccessibleButton;
