import React from 'react';

// Generic Card Component
export const Card = ({ children, className = '', hover = true }) => (
  <div
    className={`bg-white rounded-lg shadow-sm border border-slate-200 transition-all duration-200 ${
      hover ? 'hover:shadow-md' : ''
    } ${className}`}
  >
    {children}
  </div>
);

// Card with Header
export const CardHeader = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-slate-200 ${className}`}>
    {children}
  </div>
);

// Card Body
export const CardBody = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>
    {children}
  </div>
);

// Card Footer
export const CardFooter = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-lg ${className}`}>
    {children}
  </div>
);

// Stat Card for dashboard
export const StatCard = ({ label, value, icon, change, trend = 'up', className = '' }) => (
  <Card className={`${className}`}>
    <div className="px-6 py-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-600 text-sm font-medium">{label}</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-1">{value}</h3>
          {change && (
            <p
              className={`text-xs font-medium mt-2 ${
                trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend === 'up' ? '↑' : '↓'} {change}
            </p>
          )}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  </Card>
);

// Section Card with Title
export const SectionCard = ({ title, subtitle, children, action = null, className = '' }) => (
  <Card className={className}>
    <CardHeader className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </CardHeader>
    <CardBody>{children}</CardBody>
  </Card>
);

// Status Badge
export const Badge = ({ text, status = 'default', size = 'md' }) => {
  const baseStyles = 'font-medium rounded-full inline-block';
  const sizeStyles = {
    sm: 'px-2.5 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const statusStyles = {
    default: 'bg-slate-100 text-slate-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    error: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
    primary: 'bg-blue-600 text-white',
  };

  return (
    <span className={`${baseStyles} ${sizeStyles[size]} ${statusStyles[status]}`}>
      {text}
    </span>
  );
};

export default Card;
