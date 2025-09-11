import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

const MobileDrawer = ({
  isOpen,
  onClose,
  children,
  title,
  position = 'left',
  size = 'md',
  className = '',
  enableSwipe = true,
}) => {
  const drawerRef = useRef(null);
  const startX = useRef(0);
  const startY = useRef(0);
  const currentX = useRef(0);
  const currentY = useRef(0);
  const isDragging = useRef(false);

  const positionClasses = {
    left: 'left-0 top-0 h-full',
    right: 'right-0 top-0 h-full',
    top: 'top-0 left-0 w-full',
    bottom: 'bottom-0 left-0 w-full',
  };

  const sizeClasses = {
    sm: position === 'left' || position === 'right' ? 'w-80' : 'h-80',
    md: position === 'left' || position === 'right' ? 'w-96' : 'h-96',
    lg: position === 'left' || position === 'right' ? 'w-[28rem]' : 'h-[28rem]',
    full: position === 'left' || position === 'right' ? 'w-full' : 'h-full',
  };

  const transformClasses = {
    left: isOpen ? 'translate-x-0' : '-translate-x-full',
    right: isOpen ? 'translate-x-0' : 'translate-x-full',
    top: isOpen ? 'translate-y-0' : '-translate-y-full',
    bottom: isOpen ? 'translate-y-0' : 'translate-y-full',
  };

  // Handle touch events for swipe gestures
  const handleTouchStart = (e) => {
    if (!enableSwipe) return;
    
    isDragging.current = true;
    startX.current = e.touches[0].clientX;
    startY.current = e.touches[0].clientY;
    currentX.current = e.touches[0].clientX;
    currentY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e) => {
    if (!isDragging.current || !enableSwipe) return;

    currentX.current = e.touches[0].clientX;
    currentY.current = e.touches[0].clientY;

    const deltaX = currentX.current - startX.current;
    const deltaY = currentY.current - startY.current;

    // Determine swipe direction based on position
    const isHorizontalSwipe = Math.abs(deltaX) > Math.abs(deltaY);
    const isClosingSwipe = 
      (position === 'left' && deltaX < -50) ||
      (position === 'right' && deltaX > 50) ||
      (position === 'top' && deltaY < -50) ||
      (position === 'bottom' && deltaY > 50);

    if (isHorizontalSwipe && isClosingSwipe) {
      onClose();
    }
  };

  const handleTouchEnd = () => {
    isDragging.current = false;
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when drawer is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-300 ease-in-out ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div
        ref={drawerRef}
        className={`
          fixed z-50 bg-white shadow-2xl transition-all duration-300 ease-out
          ${positionClasses[position]}
          ${sizeClasses[size]}
          ${transformClasses[position]}
          ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}
          ${className}
        `}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors touch-target"
              aria-label="Close drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </>
  );
};

export default MobileDrawer;
