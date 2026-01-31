import React from 'react';
import { MapPin, Briefcase, DollarSign, Clock, ExternalLink, Bookmark } from 'lucide-react';

const JobCard = ({ job, onApply, onSave, showMatchScore = true }) => {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:border-blue-500/50 transition duration-300 group">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition">
            {job.title || 'Job Title'}
          </h3>
          <p className="text-blue-400 font-medium mt-1">{job.company || 'Company Name'}</p>
        </div>
        {showMatchScore && job.match_score && (
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            job.match_score >= 80 
              ? 'bg-green-500/20 text-green-400' 
              : job.match_score >= 60 
                ? 'bg-yellow-500/20 text-yellow-400'
                : 'bg-gray-500/20 text-gray-400'
          }`}>
            {job.match_score}% Match
          </span>
        )}
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center text-gray-400 text-sm">
          <MapPin size={16} className="mr-2 flex-shrink-0" />
          <span>{job.location || 'Location not specified'}</span>
        </div>
        <div className="flex items-center text-gray-400 text-sm">
          <Briefcase size={16} className="mr-2 flex-shrink-0" />
          <span>{job.job_type || job.type || 'Full Time'}</span>
        </div>
        {job.salary && (
          <div className="flex items-center text-gray-400 text-sm">
            <DollarSign size={16} className="mr-2 flex-shrink-0" />
            <span>{job.salary}</span>
          </div>
        )}
        {job.posted_date && (
          <div className="flex items-center text-gray-400 text-sm">
            <Clock size={16} className="mr-2 flex-shrink-0" />
            <span>Posted: {new Date(job.posted_date).toLocaleDateString()}</span>
          </div>
        )}
      </div>

      {/* Description */}
      {job.description && (
        <p className="text-gray-400 text-sm mb-4 line-clamp-3">
          {job.description}
        </p>
      )}

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {job.skills.slice(0, 5).map((skill, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-medium"
            >
              {skill}
            </span>
          ))}
          {job.skills.length > 5 && (
            <span className="px-2 py-1 text-gray-400 text-xs">
              +{job.skills.length - 5} more
            </span>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-white/10">
        <button 
          onClick={() => onApply?.(job)}
          className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition flex items-center justify-center gap-2"
        >
          Apply Now
          <ExternalLink size={16} />
        </button>
        <button 
          onClick={() => onSave?.(job)}
          className="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition"
          title="Save job"
        >
          <Bookmark size={18} />
        </button>
      </div>

      {/* Apply Link */}
      {job.apply_url && (
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block mt-3 text-center text-sm text-gray-400 hover:text-blue-400 transition"
        >
          View original posting →
        </a>
      )}
    </div>
  );
};

export default JobCard;
