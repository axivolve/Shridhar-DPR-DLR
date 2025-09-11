import React, { useEffect } from 'react';
import { X, GripHorizontal } from 'lucide-react';

const BottomSheet = ({
  isOpen,
  onClose,
  children,
  title,
  className = '',
  showHandle = true,
  snapPoints = ['50%', '90%'],
  defaultSnap = 0,
}) => {
  const [currentSnap, setCurrentSnap] = React.useState(defaultSnap);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when bottom sheet is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSnapChange = () => {
    const nextSnap = (currentSnap + 1) % snapPoints.length;
    setCurrentSnap(nextSnap);
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      onClick={handleOverlayClick}
    >
      <div
        className={`
          fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl
          transition-all duration-300 ease-out
          ${isOpen ? 'translate-y-0' : 'translate-y-full'}
          ${className}
        `}
        style={{ height: snapPoints[currentSnap] }}
      >
        {/* Handle */}
        {showHandle && (
          <div className="flex justify-center pt-3 pb-2">
            <button
              onClick={handleSnapChange}
              className="w-12 h-1 bg-gray-300 rounded-full hover:bg-gray-400 transition-colors"
              aria-label="Resize bottom sheet"
            />
          </div>
        )}
        
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors touch-target"
              aria-label="Close bottom sheet"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {children}
        </div>
      </div>
    </div>
  );
};

export default BottomSheet;
