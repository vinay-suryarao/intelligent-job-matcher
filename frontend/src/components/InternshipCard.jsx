import React from 'react';
import { MapPin, Calendar, DollarSign, Building2, Clock, Bookmark } from 'lucide-react';

const InternshipCard = ({ internship }) => {
  return (
    <div className="bg-white rounded-3xl p-8 border border-slate-200 hover:border-brand-accent hover:shadow-2xl transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex gap-4">
          <div className="w-14 h-14 bg-brand-bg rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-sm">
            <Building2 className="text-brand-dark" size={24} />
          </div>
          <div>
            <h3 className="text-xl font-black text-brand-dark tracking-tight mb-1">
              {internship.title}
            </h3>
            <p className="text-sm font-bold text-slate-400 uppercase tracking-wider">
              {internship.company}
            </p>
          </div>
        </div>
        <button className="p-2 hover:bg-brand-bg rounded-xl transition-colors">
          <Bookmark className="text-slate-300 hover:text-brand-accent" size={20} />
        </button>
      </div>

      {/* Details */}
      <div className="space-y-3 mb-6">
        <div className="flex items-center gap-3 text-sm">
          <MapPin className="text-brand-accent" size={16} />
          <span className="font-bold text-slate-600">{internship.location}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <Clock className="text-brand-accent" size={16} />
          <span className="font-bold text-slate-600">{internship.duration}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <DollarSign className="text-brand-accent" size={16} />
          <span className="font-bold text-slate-600">{internship.stipend}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <Calendar className="text-brand-accent" size={16} />
          <span className="font-bold text-slate-600">Posted: {internship.posted}</span>
        </div>
      </div>

      {/* Domain Badge */}
      <div className="mb-6">
        <span className="inline-block px-4 py-2 bg-brand-accent/10 text-brand-accent rounded-full text-xs font-black uppercase tracking-widest">
          {internship.domain}
        </span>
      </div>

      {/* Skills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {internship.skills?.map((skill, idx) => (
          <span 
            key={idx}
            className="px-3 py-1.5 bg-brand-bg text-brand-dark rounded-lg text-xs font-bold"
          >
            {skill}
          </span>
        ))}
      </div>

      {/* Action Button */}
      <button className="w-full bg-brand-dark text-white py-4 rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-brand-accent hover:text-brand-dark transition-all shadow-lg">
        Apply Now
      </button>
    </div>
  );
};

export default InternshipCard;