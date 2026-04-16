import React from 'react';

// Progress Indicator
export const ProgressIndicator = ({ percentage, label, size = 'md', showLabel = true }) => {
  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  };

  const labelSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const getColor = (percent) => {
    if (percent < 30) return 'bg-red-500';
    if (percent < 60) return 'bg-yellow-500';
    if (percent < 85) return 'bg-blue-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between mb-2">
          <span className={`${labelSizes[size]} font-medium text-slate-700`}>{label}</span>
          <span className={`${labelSizes[size]} font-semibold text-slate-900`}>{percentage}%</span>
        </div>
      )}
      <div className={`w-full bg-slate-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className={`h-full ${getColor(percentage)} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Linear Progress
export const LinearProgress = ({ current, total, label = null }) => {
  const percentage = (current / total) * 100;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2 text-sm">
          <span className="font-medium text-slate-700">{label}</span>
          <span className="text-slate-600">{current}/{total}</span>
        </div>
      )}
      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
};

// Circular Progress
export const CircularProgress = ({ percentage, size = 'md', label = null }) => {
  const sizeValues = {
    sm: { radius: 30, size: 60 },
    md: { radius: 45, size: 100 },
    lg: { radius: 60, size: 140 },
  };

  const { radius, size: svgSize } = sizeValues[size];
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg
          className="transform -rotate-90"
          style={{ width: svgSize, height: svgSize }}
          viewBox={`0 0 ${svgSize} ${svgSize}`}
        >
          {/* Background circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="4"
          />
          {/* Progress circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
        </svg>
        {/* Centered percentage */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{percentage}%</div>
            {label && <div className="text-xs text-slate-600">{label}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

// Empty State
export const EmptyState = ({ icon = '📭', title, description, action = null }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="text-6xl mb-4">{icon}</div>
    <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
    <p className="text-slate-600 text-sm mb-6 max-w-xs">{description}</p>
    {action && <div>{action}</div>}
  </div>
);

// Loading Skeleton
export const Skeleton = ({ className = '', count = 1 }) => {
  return (
    <div className="space-y-3">
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-slate-200 rounded ${className || 'h-12'}`}
        />
      ))}
    </div>
  );
};

// Alert Box
export const Alert = ({ type = 'info', title, message, onClose = null }) => {
  const typeStyles = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  };

  const iconMap = {
    info: 'ℹ️',
    success: '✓',
    warning: '⚠️',
    error: '✕',
  };

  return (
    <div className={`border rounded-lg p-4 flex items-start gap-3 ${typeStyles[type]}`}>
      <span className="text-lg mt-0.5">{iconMap[type]}</span>
      <div className="flex-1">
        {title && <h4 className="font-semibold text-sm mb-1">{title}</h4>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-lg hover:opacity-70 transition-opacity"
        >
          ✕
        </button>
      )}
    </div>
  );
};

export default ProgressIndicator;
