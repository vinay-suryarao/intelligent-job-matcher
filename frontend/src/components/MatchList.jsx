import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Building2, MapPin, DollarSign, Briefcase, TrendingUp, Star, ArrowRight, Bookmark, RefreshCw, ExternalLink, CheckCircle } from 'lucide-react';

const MatchList = () => {
  const [matchedJobs, setMatchedJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const data = await api.getJobMatches(20);
      if (data.matches) {
        setMatchedJobs(data.matches);
      }
    } catch (err) {
      console.error('Error fetching matches:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMatchColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-brand-accent';
    return 'bg-yellow-500';
  };

  const getMatchTextColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-brand-accent';
    return 'text-yellow-600';
  };

  return (
    <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-black text-brand-dark tracking-tight uppercase mb-2">
            Matched Jobs
          </h2>
          <p className="text-slate-400 font-medium text-sm">
            Real-time job matches based on your skills
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={fetchMatches} className="p-2 rounded-xl bg-brand-bg hover:bg-brand-accent hover:text-white transition-all">
            <RefreshCw size={18} />
          </button>
          <div className="bg-brand-accent/10 px-6 py-3 rounded-2xl border border-brand-accent/20">
            <p className="text-xs font-black text-brand-accent uppercase tracking-widest">
              {matchedJobs.length} Matches
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-brand-accent border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : matchedJobs.length === 0 ? (
        <div className="text-center py-16">
          <Briefcase className="mx-auto text-brand-accent mb-4" size={48} />
          <h3 className="text-xl font-black text-brand-dark mb-2">No Matches Found</h3>
          <p className="text-slate-400">Upload your resume to get personalized matches</p>
        </div>
      ) : (
        <div className="space-y-4">
          {matchedJobs.map((match, index) => (
            <div 
              key={match.job?.id || index}
              className="bg-brand-bg/30 border border-slate-200 rounded-3xl p-6 hover:border-brand-accent hover:shadow-xl transition-all duration-300 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex gap-4 flex-1">
                  {/* Company Logo */}
                  <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm border border-slate-100 group-hover:scale-110 transition-transform">
                    <Building2 className="text-brand-dark" size={24} />
                  </div>

                  {/* Job Details */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-black text-brand-dark tracking-tight mb-1">
                          {match.job?.title || 'Job Title'}
                        </h3>
                        <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">
                          {match.job?.company || 'Company'}
                        </p>
                      </div>
                    </div>

                    {/* Info Grid */}
                    <div className="grid grid-cols-3 gap-4 mt-4 mb-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="text-brand-accent" size={16} />
                        <span className="text-sm font-bold text-slate-600">{match.job?.location || 'Remote'}</span>
                      </div>
                      {match.job?.salary && (
                        <div className="flex items-center gap-2">
                          <DollarSign className="text-brand-accent" size={16} />
                          <span className="text-sm font-bold text-slate-600">{match.job.salary}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <Briefcase className="text-brand-accent" size={16} />
                        <span className="text-sm font-bold text-slate-600">{match.job?.type || 'Full Time'}</span>
                      </div>
                    </div>

                    {/* Skills - Matched & Missing */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {(match.skill_match?.matched || []).slice(0, 4).map((skill, idx) => (
                        <span key={idx} className="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-xs font-bold flex items-center gap-1">
                          <CheckCircle size={10} /> {skill}
                        </span>
                      ))}
                      {(match.skill_match?.missing || []).slice(0, 3).map((skill, idx) => (
                        <span key={idx} className="px-3 py-1.5 bg-red-100 text-red-600 rounded-lg text-xs font-bold">
                          ✗ {skill}
                        </span>
                      ))}
                      {(match.job?.skills || [])
                        .filter(s => !match.skill_match?.matched?.includes(s) && !match.skill_match?.missing?.includes(s))
                        .slice(0, 2)
                        .map((skill, idx) => (
                          <span key={idx} className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-xs font-bold">
                            {skill}
                          </span>
                        ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Match Score & Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                <div className="flex items-center gap-6">
                  {/* Match Score */}
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-16 h-16 rounded-full bg-white border-4 border-slate-100 flex items-center justify-center">
                        <span className={`text-xl font-black ${getMatchTextColor(match.match_score)}`}>
                          {match.match_score?.toFixed(0) || 0}
                        </span>
                      </div>
                      <div className={`absolute -top-1 -right-1 w-6 h-6 rounded-full ${getMatchColor(match.match_score)} flex items-center justify-center shadow-lg`}>
                        <Star className="text-white fill-white" size={12} />
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-black text-slate-400 uppercase tracking-widest">
                        Match Score
                      </p>
                      <p className={`text-sm font-black ${getMatchTextColor(match.match_score)}`}>
                        {match.match_score >= 90 ? 'Excellent Match' : match.match_score >= 75 ? 'Great Match' : 'Good Match'}
                      </p>
                    </div>
                  </div>

                  {/* Match Indicator Bar */}
                  <div className="flex-1 max-w-xs">
                    <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${getMatchColor(match.match_score)} rounded-full transition-all duration-500`}
                        style={{ width: `${match.match_score || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Apply Button */}
                <a 
                  href={match.job?.apply_url || match.job?.url || '#'} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-brand-dark text-white px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-brand-accent hover:text-white transition-all shadow-lg flex items-center gap-2 group-hover:scale-105"
                >
                  Apply Now
                  <ExternalLink size={16} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MatchList;