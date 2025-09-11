import React, { useState, useRef } from 'react';
import Skeleton from './Skeleton';

const OptimizedImage = ({
  src,
  alt,
  className = '',
  fallback = null,
  lazy = true,
  ...props
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef(null);

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const imageElement = (
    <img
      ref={imgRef}
      src={src}
      alt={alt}
      className={`transition-opacity duration-300 ${
        isLoading ? 'opacity-0' : 'opacity-100'
      } ${className}`}
      onLoad={handleLoad}
      onError={handleError}
      loading={lazy ? 'lazy' : 'eager'}
      {...props}
    />
  );

  if (hasError) {
    return fallback || (
      <div className={`bg-gray-200 flex items-center justify-center ${className}`}>
        <span className="text-gray-500 text-sm">Image not available</span>
      </div>
    );
  }

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0">
          <Skeleton className="w-full h-full" />
        </div>
      )}
      {imageElement}
    </div>
  );
};

export default OptimizedImage;
