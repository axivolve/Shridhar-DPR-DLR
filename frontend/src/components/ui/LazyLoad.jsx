import React, { useState, useRef, useEffect } from 'react';
import Skeleton from './Skeleton';

const LazyLoad = ({
  children,
  fallback,
  threshold = 0.1,
  rootMargin = '50px',
  className = '',
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          setHasLoaded(true);
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, [threshold, rootMargin]);

  return (
    <div ref={elementRef} className={className} {...props}>
      {isVisible ? (
        hasLoaded ? children : (
          <div className="animate-pulse">
            {fallback || <Skeleton className="h-32 w-full" />}
          </div>
        )
      ) : (
        fallback || <Skeleton className="h-32 w-full" />
      )}
    </div>
  );
};

export default LazyLoad;
