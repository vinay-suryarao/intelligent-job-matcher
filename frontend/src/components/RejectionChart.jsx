import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { XCircle, AlertCircle } from 'lucide-react';

const RejectionChart = () => {
  // Sample data for rejection reasons
  const rejectionData = [
    { name: 'Skills Mismatch', value: 35, color: '#ef4444' },
    { name: 'Experience Gap', value: 25, color: '#f97316' },
    { name: 'Location Issues', value: 15, color: '#f59e0b' },
    { name: 'Salary Expectations', value: 12, color: '#eab308' },
    { name: 'Culture Fit', value: 8, color: '#84cc16' },
    { name: 'Other Reasons', value: 5, color: '#22c55e' }
  ];

  const totalRejections = rejectionData.reduce((sum, item) => sum + item.value, 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xl">
          <p className="text-sm font-black text-brand-dark uppercase tracking-wide">
            {payload[0].name}
          </p>
          <p className="text-2xl font-black text-brand-accent mt-1">
            {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-sm">
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-red-50 p-3 rounded-2xl">
              <XCircle className="text-red-500" size={24} />
            </div>
            <h2 className="text-3xl font-black text-brand-dark uppercase tracking-tight">
              Rejection Analysis
            </h2>
          </div>
          <p className="text-slate-400 font-medium text-sm">
            Understanding why applications didn't succeed
          </p>
        </div>
        <div className="bg-red-50 px-6 py-3 rounded-2xl border border-red-100">
          <p className="text-xs font-black text-red-600 uppercase tracking-widest">
            Total: {totalRejections}% Analyzed
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-10">
        {/* Chart */}
        <div className="flex items-center justify-center">
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={rejectionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                  animationDuration={1500}
                >
                  {rejectionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Legend with details */}
        <div className="space-y-3">
          {rejectionData.map((item, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-4 rounded-2xl bg-brand-bg/50 hover:bg-brand-bg transition-all group"
            >
              <div className="flex items-center gap-3 flex-1">
                <div 
                  className="w-4 h-4 rounded-lg group-hover:scale-125 transition-transform"
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="font-bold text-brand-dark text-sm">
                  {item.name}
                </span>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-2 bg-slate-200 rounded-full w-24 overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ 
                      width: `${item.value}%`,
                      backgroundColor: item.color 
                    }}
                  ></div>
                </div>
                <span className="font-black text-xl min-w-[50px] text-right" style={{ color: item.color }}>
                  {item.value}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="mt-8 pt-8 border-t border-slate-100">
        <div className="flex items-start gap-3 bg-blue-50 p-6 rounded-2xl border border-blue-100">
          <AlertCircle className="text-blue-500 flex-shrink-0 mt-1" size={20} />
          <div>
            <p className="text-sm font-black text-blue-900 uppercase tracking-wide mb-2">
              Key Insight
            </p>
            <p className="text-sm font-medium text-blue-700">
              Skills mismatch is the primary rejection reason. Focus on upskilling in high-demand technologies 
              to improve your application success rate by up to 35%.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RejectionChart;