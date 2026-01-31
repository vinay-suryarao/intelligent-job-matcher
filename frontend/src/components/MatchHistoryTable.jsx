import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Calendar, Building2, MapPin, TrendingUp, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';

const MatchHistoryTable = () => {
  const [matchHistory, setMatchHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatchHistory();
  }, []);

  const fetchMatchHistory = async () => {
    setLoading(true);
    try {
      // Fetch job matches from backend
      const data = await api.getJobMatches(50);
      if (data.matches) {
        // Transform matches into history format
        const history = data.matches.map((match, index) => ({
          id: match.job?.id || index,
          jobTitle: match.job?.title || 'Unknown Job',
          company: match.job?.company || 'Unknown Company',
          location: match.job?.location || 'Remote',
          matchScore: match.match_score || 0,
          appliedDate: match.matched_at || new Date().toISOString(),
          status: getStatusFromScore(match.match_score, match.rejection_probability),
          statusColor: getStatusColor(match.match_score, match.rejection_probability),
          apply_url: match.job?.apply_url || match.job?.url
        }));
        setMatchHistory(history);
      }
    } catch (err) {
      console.error('Error fetching match history:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusFromScore = (score, rejectionProb) => {
    if (score >= 90 && (!rejectionProb || rejectionProb < 20)) return 'High Match';
    if (score >= 75) return 'Good Match';
    if (score >= 60) return 'Moderate';
    return 'Low Match';
  };

  const getStatusColor = (score, rejectionProb) => {
    if (score >= 90 && (!rejectionProb || rejectionProb < 20)) return 'green';
    if (score >= 75) return 'blue';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'High Match':
        return <CheckCircle className="text-green-500" size={18} />;
      case 'Low Match':
        return <XCircle className="text-red-500" size={18} />;
      case 'Moderate':
        return <Clock className="text-yellow-500" size={18} />;
      default:
        return <TrendingUp className="text-blue-500" size={18} />;
    }
  };

  const getStatusBadge = (status, color) => {
    const colorClasses = {
      green: 'bg-green-50 text-green-600 border-green-200',
      red: 'bg-red-50 text-red-600 border-red-200',
      blue: 'bg-blue-50 text-blue-600 border-blue-200',
      yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200'
    };

    return (
      <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest border ${colorClasses[color]}`}>
        {getStatusIcon(status)}
        {status}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-black text-brand-dark tracking-tight uppercase mb-2">
            Match History
          </h2>
          <p className="text-slate-400 font-medium text-sm">
            Your job matches and their status (Real-time data)
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={fetchMatchHistory} className="p-2 rounded-xl bg-brand-bg hover:bg-brand-accent hover:text-white transition-all">
            <RefreshCw size={18} />
          </button>
          <div className="bg-brand-bg px-6 py-3 rounded-2xl">
            <p className="text-xs font-black text-slate-600 uppercase tracking-widest">
              Total: {matchHistory.length} Matches
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-brand-accent border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : matchHistory.length === 0 ? (
        <div className="text-center py-16">
          <Building2 className="mx-auto text-brand-accent mb-4" size={48} />
          <h3 className="text-xl font-black text-brand-dark mb-2">No Matches Yet</h3>
          <p className="text-slate-400">Your job matches will appear here</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
          <thead>
            <tr className="border-b-2 border-slate-100">
              <th className="text-left py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Job Title
              </th>
              <th className="text-left py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Company
              </th>
              <th className="text-left py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Location
              </th>
              <th className="text-center py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Match Score
              </th>
              <th className="text-left py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Applied Date
              </th>
              <th className="text-center py-4 px-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {matchHistory.map((item) => (
              <tr 
                key={item.id} 
                className="border-b border-slate-100 hover:bg-brand-bg/30 transition-colors group"
              >
                <td className="py-5 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-brand-dark rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Building2 className="text-white" size={18} />
                    </div>
                    <span className="font-bold text-brand-dark text-sm">
                      {item.jobTitle}
                    </span>
                  </div>
                </td>
                <td className="py-5 px-4">
                  <span className="font-bold text-slate-600 text-sm">
                    {item.company}
                  </span>
                </td>
                <td className="py-5 px-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="text-brand-accent" size={14} />
                    <span className="font-medium text-slate-500 text-sm">
                      {item.location}
                    </span>
                  </div>
                </td>
                <td className="py-5 px-4 text-center">
                  <div className="inline-flex items-center gap-2 bg-brand-accent/10 px-4 py-2 rounded-xl">
                    <TrendingUp className="text-brand-accent" size={16} />
                    <span className="font-black text-brand-accent text-sm">
                      {item.matchScore}%
                    </span>
                  </div>
                </td>
                <td className="py-5 px-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="text-slate-400" size={14} />
                    <span className="font-medium text-slate-500 text-sm">
                      {new Date(item.appliedDate).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                      })}
                    </span>
                  </div>
                </td>
                <td className="py-5 px-4 text-center">
                  {getStatusBadge(item.status, item.statusColor)}
                </td>
              </tr>
            ))}
          </tbody>
          </table>
        </div>

        {/* Summary Stats */}
        <div className="mt-8 pt-6 border-t border-slate-100 grid grid-cols-4 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-2xl border border-green-100">
            <p className="text-2xl font-black text-green-600">
              {matchHistory.filter(item => item.status === 'High Match').length}
            </p>
            <p className="text-xs font-bold text-green-600 uppercase tracking-widest mt-1">
              High Match
            </p>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-2xl border border-blue-100">
            <p className="text-2xl font-black text-blue-600">
              {matchHistory.filter(item => item.status === 'Good Match').length}
            </p>
            <p className="text-xs font-bold text-blue-600 uppercase tracking-widest mt-1">
              Good Match
            </p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-2xl border border-yellow-100">
            <p className="text-2xl font-black text-yellow-600">
              {matchHistory.filter(item => item.status === 'Moderate').length}
            </p>
            <p className="text-xs font-bold text-yellow-600 uppercase tracking-widest mt-1">
              Moderate
            </p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-2xl border border-red-100">
            <p className="text-2xl font-black text-red-600">
              {matchHistory.filter(item => item.status === 'Low Match').length}
            </p>
            <p className="text-xs font-bold text-red-600 uppercase tracking-widest mt-1">
              Low Match
            </p>
          </div>
        </div>
        </>
      )}
    </div>
  );
};

export default MatchHistoryTable;