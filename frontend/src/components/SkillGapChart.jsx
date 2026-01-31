import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, Target } from 'lucide-react';

const SkillGapChart = () => {
  // Sample data for missing skills
  const skillGapData = [
    { skill: 'TypeScript', gap: 85, color: '#3b82f6' },
    { skill: 'Docker', gap: 78, color: '#8b5cf6' },
    { skill: 'Kubernetes', gap: 72, color: '#ec4899' },
    { skill: 'GraphQL', gap: 68, color: '#f59e0b' },
    { skill: 'AWS', gap: 65, color: '#10b981' },
    { skill: 'MongoDB', gap: 58, color: '#06b6d4' },
    { skill: 'Redis', gap: 52, color: '#ef4444' },
    { skill: 'Next.js', gap: 45, color: '#8b5cf6' }
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xl">
          <p className="text-sm font-black text-brand-dark uppercase tracking-wide">
            {payload[0].payload.skill}
          </p>
          <p className="text-2xl font-black text-brand-accent mt-1">
            {payload[0].value}% Demand
          </p>
        </div>
      );
    }
    return null;
  };

  // Get bar color based on gap level
  const getBarColor = (gap) => {
    if (gap >= 75) return '#ef4444'; // Red for high demand
    if (gap >= 60) return '#f97316'; // Orange for medium-high
    if (gap >= 45) return '#f59e0b'; // Yellow for medium
    return '#22c55e'; // Green for lower priority
  };

  return (
    <div className="bg-white p-10 rounded-[3.5rem] border border-slate-100 shadow-sm">
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-accent/10 p-3 rounded-2xl">
              <Target className="text-brand-accent" size={24} />
            </div>
            <h2 className="text-3xl font-black text-brand-dark uppercase tracking-tight">
              Skill Gap Analysis
            </h2>
          </div>
          <p className="text-slate-400 font-medium text-sm">
            Top missing skills in demand by employers
          </p>
        </div>
        <div className="bg-brand-accent/10 px-6 py-3 rounded-2xl border border-brand-accent/20">
          <p className="text-xs font-black text-brand-accent uppercase tracking-widest">
            {skillGapData.length} Skills Identified
          </p>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="h-[350px] w-full mb-8">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={skillGapData} 
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            barSize={40}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis 
              dataKey="skill" 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fill: '#64748b', fontSize: 12, fontWeight: 'bold' }}
            />
            <YAxis 
              tick={{ fill: '#cbd5e1', fontSize: 12, fontWeight: 'bold' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 159, 86, 0.1)' }} />
            <Bar 
              dataKey="gap" 
              radius={[12, 12, 0, 0]}
              animationDuration={1500}
            >
              {skillGapData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.gap)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Priority Skills */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-red-50 to-orange-50 p-6 rounded-2xl border border-red-100">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-red-500 p-2 rounded-xl">
              <TrendingUp className="text-white" size={18} />
            </div>
            <p className="text-xs font-black text-red-900 uppercase tracking-widest">
              Highest Priority
            </p>
          </div>
          <div className="space-y-2">
            {skillGapData.slice(0, 3).map((skill, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="font-bold text-red-900 text-sm">{skill.skill}</span>
                <span className="font-black text-red-600 text-lg">{skill.gap}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-500 p-2 rounded-xl">
              <Target className="text-white" size={18} />
            </div>
            <p className="text-xs font-black text-blue-900 uppercase tracking-widest">
              Learning Recommendation
            </p>
          </div>
          <p className="font-medium text-blue-700 text-sm leading-relaxed">
            Focus on TypeScript and Docker first - they appear in 85% and 78% of job requirements respectively. 
            Mastering these will significantly improve your match scores.
          </p>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="mt-6 pt-6 border-t border-slate-100">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-black text-slate-400 uppercase tracking-widest">
            Overall Skill Coverage
          </p>
          <p className="text-lg font-black text-brand-dark">
            42<span className="text-slate-300">/100</span>
          </p>
        </div>
        <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-brand-accent to-red-500 rounded-full transition-all duration-1000"
            style={{ width: '42%' }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default SkillGapChart;