import React from 'react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({ title, value, change, icon }) => {
  const isPositive = change && change >= 0;
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        {icon && <span className="text-gray-400">{icon}</span>}
      </div>
      <div className="flex items-baseline gap-2">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {change !== undefined && (
          <span className={`text-sm font-medium ${isPositive ? 'text-success' : 'text-danger'}`}>
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </span>
        )}
      </div>
    </div>
  );
};
