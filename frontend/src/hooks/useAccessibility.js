import { useEffect, useRef } from 'react';

// Hook for managing focus and keyboard navigation
export const useFocusManagement = (isActive = true) => {
  const focusableElementsRef = useRef([]);
  const currentIndexRef = useRef(0);

  const updateFocusableElements = (container) => {
    if (!container) return;
    
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ');
    
    focusableElementsRef.current = Array.from(
      container.querySelectorAll(focusableSelectors)
    );
  };

  const handleKeyDown = (e) => {
    if (!isActive || focusableElementsRef.current.length === 0) return;

    const { key } = e;
    const currentIndex = currentIndexRef.current;
    const elements = focusableElementsRef.current;

    switch (key) {
      case 'Tab':
        e.preventDefault();
        if (e.shiftKey) {
          currentIndexRef.current = currentIndex > 0 ? currentIndex - 1 : elements.length - 1;
        } else {
          currentIndexRef.current = currentIndex < elements.length - 1 ? currentIndex + 1 : 0;
        }
        elements[currentIndexRef.current]?.focus();
        break;
      
      case 'Enter':
      case ' ':
        e.preventDefault();
        elements[currentIndex]?.click();
        break;
      
      case 'Escape':
        e.preventDefault();
        // Close modal or return focus to trigger
        const activeElement = document.activeElement;
        if (activeElement && activeElement.blur) {
          activeElement.blur();
        }
        break;
    }
  };

  return {
    updateFocusableElements,
    handleKeyDown,
    focusableElements: focusableElementsRef.current
  };
};

// Hook for screen reader announcements
export const useScreenReader = () => {
  const announce = (message, priority = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return { announce };
};

// Hook for keyboard shortcuts
export const useKeyboardShortcuts = (shortcuts = {}) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase();
      const modifiers = {
        ctrl: e.ctrlKey,
        alt: e.altKey,
        shift: e.shiftKey,
        meta: e.metaKey
      };

      const shortcutKey = Object.keys(shortcuts).find(shortcut => {
        const [keyPart, ...modifierParts] = shortcut.split('+').reverse();
        return keyPart === key && 
               modifierParts.every(mod => modifiers[mod.toLowerCase()]);
      });

      if (shortcutKey) {
        e.preventDefault();
        shortcuts[shortcutKey]();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
};

// Hook for ARIA attributes
export const useAriaAttributes = (props = {}) => {
  const {
    role,
    ariaLabel,
    ariaLabelledBy,
    ariaDescribedBy,
    ariaExpanded,
    ariaSelected,
    ariaChecked,
    ariaDisabled,
    ariaHidden,
    ...otherProps
  } = props;

  const ariaProps = {
    ...(role && { role }),
    ...(ariaLabel && { 'aria-label': ariaLabel }),
    ...(ariaLabelledBy && { 'aria-labelledby': ariaLabelledBy }),
    ...(ariaDescribedBy && { 'aria-describedby': ariaDescribedBy }),
    ...(ariaExpanded !== undefined && { 'aria-expanded': ariaExpanded }),
    ...(ariaSelected !== undefined && { 'aria-selected': ariaSelected }),
    ...(ariaChecked !== undefined && { 'aria-checked': ariaChecked }),
    ...(ariaDisabled !== undefined && { 'aria-disabled': ariaDisabled }),
    ...(ariaHidden !== undefined && { 'aria-hidden': ariaHidden }),
  };

  return {
    ariaProps,
    otherProps
  };
};
