import React from 'react';

const LoadingSpinner = ({ size = 'md', className = '', text = '' }) => {
  const sizes = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
    xl: 'h-24 w-24'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`animate-spin rounded-full border-t-2 border-b-2 border-blue-500 ${sizes[size]}`}></div>
      {text && (
        <p className="mt-4 text-gray-400 text-sm">{text}</p>
      )}
    </div>
  );
};

// Full page loading spinner
export const FullPageLoader = ({ text = 'Loading...' }) => (
  <div className="fixed inset-0 bg-gray-900 flex items-center justify-center z-50">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-400">{text}</p>
    </div>
  </div>
);

// Inline loading spinner
export const InlineLoader = ({ size = 'sm' }) => (
  <LoadingSpinner size={size} className="inline-block" />
);

// Skeleton loader for content
export const SkeletonLoader = ({ className = '', lines = 3 }) => (
  <div className={`animate-pulse ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <div
        key={i}
        className={`h-4 bg-gray-700 rounded mb-2 ${
          i === lines - 1 ? 'w-3/4' : 'w-full'
        }`}
      />
    ))}
  </div>
);

export default LoadingSpinner;
