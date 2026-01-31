import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const StatisticsCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'neutral', // 'increase' | 'decrease' | 'neutral'
  icon: Icon,
  subtitle,
  className = '' 
}) => {
  const changeColors = {
    increase: 'text-green-400',
    decrease: 'text-red-400',
    neutral: 'text-gray-400'
  };

  const changeIcons = {
    increase: TrendingUp,
    decrease: TrendingDown,
    neutral: Minus
  };

  const ChangeIcon = changeIcons[changeType];

  return (
    <div className={`bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 ${className}`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-white mt-1">{value}</h3>
        </div>
        {Icon && (
          <div className="p-3 bg-blue-500/20 rounded-xl">
            <Icon className="text-blue-400" size={24} />
          </div>
        )}
      </div>
      
      {(change !== undefined || subtitle) && (
        <div className="flex items-center gap-2">
          {change !== undefined && (
            <>
              <ChangeIcon className={changeColors[changeType]} size={16} />
              <span className={`text-sm font-medium ${changeColors[changeType]}`}>
                {change > 0 ? '+' : ''}{change}%
              </span>
            </>
          )}
          {subtitle && (
            <span className="text-gray-400 text-sm">{subtitle}</span>
          )}
        </div>
      )}
    </div>
  );
};

// Mini stat card for inline use
export const MiniStatCard = ({ label, value, icon: Icon }) => (
  <div className="flex items-center gap-3 bg-white/5 rounded-lg p-3">
    {Icon && <Icon className="text-blue-400" size={20} />}
    <div>
      <p className="text-gray-400 text-xs">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  </div>
);

// Stats grid for dashboard
export const StatsGrid = ({ stats, columns = 4 }) => (
  <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${columns} gap-6`}>
    {stats.map((stat, index) => (
      <StatisticsCard key={index} {...stat} />
    ))}
  </div>
);

export default StatisticsCard;
