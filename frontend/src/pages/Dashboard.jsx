import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import { 
  Briefcase, Target, TrendingUp, Zap, ExternalLink, 
  RefreshCw, MessageCircle, Award, AlertTriangle, CheckCircle
} from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [profileData, matchesData, statsData] = await Promise.all([
        api.getProfile(),
        api.getJobMatches(50),
        api.getStatistics(),
      ]);

      if (profileData && !profileData.error) setProfile(profileData);
      
      if (matchesData && matchesData.matches) {
        const filteredMatches = matchesData.matches
          .filter(m => m.match_score >= 70 && m.match_score <= 100)
          .slice(0, 10);
        setMatches(filteredMatches);
      }
      
      if (statsData && !statsData.error) setStats(statsData);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-brand-bg">
        <Sidebar />
        <main className="flex-1 ml-64 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-brand-accent border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-slate-500 font-bold uppercase tracking-widest text-sm">Loading...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-brand-bg">
      <Sidebar />
      
      {/* Chat Button */}
      <button 
        onClick={() => setShowChat(true)}
        className="fixed bottom-8 right-8 p-4 rounded-full bg-brand-accent text-white shadow-lg shadow-brand-accent/30 hover:scale-110 transition-transform z-50"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat Interface */}
      {showChat && (
        <ChatInterface onClose={() => setShowChat(false)} />
      )}

      <main className="flex-1 ml-64 p-10">
        <div className="flex justify-between items-start mb-10">
          <div>
            <h1 className="text-5xl font-black text-brand-dark tracking-tighter uppercase mb-2">Dashboard</h1>
            <p className="text-slate-400 font-medium text-lg">
              Welcome back, <span className="text-brand-accent font-bold">{profile?.full_name || user?.full_name || 'User'}</span>
            </p>
          </div>
          <button onClick={fetchAllData} className="p-3 rounded-2xl bg-white text-brand-dark hover:bg-brand-accent hover:text-white transition-all shadow-sm">
            <RefreshCw size={20} />
          </button>
        </div>

        <div className="grid grid-cols-4 gap-6 mb-10">
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 flex items-center justify-center">
                <Briefcase className="text-blue-500" size={24} />
              </div>
              <div>
                <p className="text-3xl font-black text-brand-dark">{stats?.total_jobs || 0}</p>
                <p className="text-slate-400 font-bold text-sm uppercase tracking-wider">Total Jobs</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-green-50 flex items-center justify-center">
                <Target className="text-green-500" size={24} />
              </div>
              <div>
                <p className="text-3xl font-black text-brand-dark">{matches.length}</p>
                <p className="text-slate-400 font-bold text-sm uppercase tracking-wider">Your Matches</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-purple-50 flex items-center justify-center">
                <TrendingUp className="text-purple-500" size={24} />
              </div>
              <div>
                <p className="text-3xl font-black text-brand-dark">{stats?.total_internships || 0}</p>
                <p className="text-slate-400 font-bold text-sm uppercase tracking-wider">Internships</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-orange-50 flex items-center justify-center">
                <Zap className="text-brand-accent" size={24} />
              </div>
              <div>
                <p className="text-3xl font-black text-brand-dark">{profile?.skills?.length || 0}</p>
                <p className="text-slate-400 font-bold text-sm uppercase tracking-wider">Your Skills</p>
              </div>
            </div>
          </div>
        </div>

        {profile?.skills && profile.skills.length > 0 && (
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-10">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-4 flex items-center gap-2">
              <Award className="text-brand-accent" size={20} /> Your Skills
            </h2>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill, i) => (
                <span key={i} className="px-4 py-2 bg-brand-bg text-brand-dark rounded-xl font-bold text-sm border border-slate-200">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight flex items-center gap-2">
              <Target className="text-brand-accent" size={20} /> Perfect Matches (70-100%)
            </h2>
            <span className="text-slate-400 text-sm font-bold">Showing {matches.length} best matches</span>
          </div>

          {matches.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-24 h-24 rounded-full bg-brand-bg flex items-center justify-center mx-auto mb-6">
                <Target className="text-brand-accent" size={40} />
              </div>
              <h3 className="text-2xl font-black text-brand-dark mb-2">No Matches Yet</h3>
              <p className="text-slate-400 mb-6">Complete your profile to get personalized job matches!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {matches.map((match, index) => (
                <div key={match.job?.id || index} className="bg-brand-bg rounded-2xl p-6 border border-slate-200 hover:border-brand-accent transition-all group">
                  <div className="flex justify-between items-start mb-4">
                    <div className={`px-4 py-2 rounded-xl font-black text-sm ${
                      match.match_score >= 90 ? 'bg-green-100 text-green-700' :
                      match.match_score >= 80 ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'
                    }`}>
                      {match.match_score?.toFixed(0)}% Match
                    </div>
                    {match.rejection_probability > 30 && (
                      <div className="flex items-center gap-1 text-yellow-600 text-sm font-bold">
                        <AlertTriangle size={14} /> {match.rejection_probability?.toFixed(0)}% Risk
                      </div>
                    )}
                  </div>

                  <h3 className="font-black text-brand-dark text-lg mb-2 group-hover:text-brand-accent transition-colors">{match.job?.title}</h3>
                  <p className="text-slate-500 font-medium mb-1">🏢 {match.job?.company}</p>
                  <p className="text-slate-400 text-sm mb-3">📍 {match.job?.location}</p>
                  {match.job?.salary && <p className="text-green-600 font-bold mb-4">💰 {match.job.salary}</p>}

                  <div className="mb-4">
                    {/* Matched Skills */}
                    {(match.skill_match?.matched || []).length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {(match.skill_match?.matched || []).slice(0, 5).map((skill, i) => (
                          <span key={i} className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-bold flex items-center gap-1">
                            <CheckCircle size={10} /> {skill}
                          </span>
                        ))}
                      </div>
                    )}
                    {/* Missing Skills */}
                    {match.skill_match?.missing?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {match.skill_match.missing.slice(0, 4).map((skill, i) => (
                          <span key={i} className="px-2 py-1 bg-red-100 text-red-600 rounded-lg text-xs font-bold">✗ {skill}</span>
                        ))}
                      </div>
                    )}
                    {/* Job Required Skills (not in matched/missing) */}
                    {match.job?.skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {match.job.skills
                          .filter(s => !match.skill_match?.matched?.includes(s) && !match.skill_match?.missing?.includes(s))
                          .slice(0, 3)
                          .map((skill, i) => (
                            <span key={i} className="px-2 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-bold">📌 {skill}</span>
                          ))}
                      </div>
                    )}
                  </div>

                  <a href={match.job?.apply_url || match.job?.url || '#'} target="_blank" rel="noopener noreferrer"
                    className="w-full flex items-center justify-center gap-2 bg-brand-dark text-white py-3 rounded-xl font-bold uppercase tracking-widest text-sm hover:bg-brand-accent transition-colors">
                    Apply Now <ExternalLink size={14} />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
