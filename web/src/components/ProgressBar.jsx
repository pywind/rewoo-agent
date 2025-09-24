import React from 'react';

const ProgressBar = ({ 
  progress = 0, 
  message = '', 
  showPercentage = true, 
  className = '',
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2', 
    lg: 'h-3'
  };

  return (
    <div className={`w-full ${className}`}>
      {(message || showPercentage) && (
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span className="truncate">{message}</span>
          {showPercentage && <span className="ml-2 flex-shrink-0">{Math.round(progress)}%</span>}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500 ease-out ${sizeClasses[size]}`}
          style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
        >
          {/* Optional shimmer effect for active progress */}
          {progress > 0 && progress < 100 && (
            <div className="h-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;