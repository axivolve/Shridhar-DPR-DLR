// Utility function to create haptic feedback
export const triggerHaptic = (type = 'light') => {
  if ('vibrate' in navigator) {
    switch (type) {
      case 'light':
        navigator.vibrate(10);
        break;
      case 'medium':
        navigator.vibrate(50);
        break;
      case 'heavy':
        navigator.vibrate([50, 30, 50]);
        break;
      case 'success':
        navigator.vibrate([50, 30, 50, 30, 50]);
        break;
      case 'error':
        navigator.vibrate([100, 50, 100]);
        break;
    }
  }
};
