import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import api from '../services/api';
import { Search, MapPin, ExternalLink, Briefcase, DollarSign, Clock, CheckCircle, AlertTriangle, MessageCircle } from 'lucide-react';

const Jobs = () => {
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('matches');
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchData();
  }, [viewMode]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (viewMode === 'matches') {
        const data = await api.getJobMatches(100);
        if (data.matches) setMatches(data.matches);
      } else {
        const data = await api.getJobs(200);
        if (data.jobs) setJobs(data.jobs);
      }
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const displayData = viewMode === 'matches' ? matches : jobs;
  
  const filteredData = displayData.filter(item => {
    const job = viewMode === 'matches' ? item.job : item;
    const matchesSearch = !searchTerm || 
      job?.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job?.company?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !locationFilter || 
      job?.location?.toLowerCase().includes(locationFilter.toLowerCase());
    return matchesSearch && matchesLocation;
  });

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
            <h1 className="text-5xl font-black text-brand-dark tracking-tighter uppercase mb-2">Jobs</h1>
            <p className="text-slate-400 font-medium text-lg">Find your dream job opportunity</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-3xl p-2 mb-8 inline-flex gap-2 shadow-sm border border-slate-200">
          <button
            onClick={() => setViewMode('matches')}
            className={`px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest transition-all ${
              viewMode === 'matches' ? 'bg-brand-dark text-white shadow-lg' : 'text-slate-400 hover:text-brand-dark'
            }`}
          >
            🎯 My Matches
          </button>
          <button
            onClick={() => setViewMode('all')}
            className={`px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest transition-all ${
              viewMode === 'all' ? 'bg-brand-dark text-white shadow-lg' : 'text-slate-400 hover:text-brand-dark'
            }`}
          >
            📋 All Jobs
          </button>
        </div>

        {/* Search & Filter */}
        <div className="flex gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search jobs by title or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
            />
          </div>
          <div className="relative w-64">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Filter by location..."
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-16 h-16 border-4 border-brand-accent border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredData.map((item, index) => {
              const job = viewMode === 'matches' ? item.job : item;
              const matchScore = item.match_score;
              const skillMatch = item.skill_match;

              return (
                <div key={job?.id || index} className="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100 hover:border-brand-accent transition-all group">
                  {matchScore && (
                    <div className={`p-3 text-center font-black text-sm uppercase tracking-widest ${
                      matchScore >= 80 ? 'bg-green-500 text-white' :
                      matchScore >= 60 ? 'bg-yellow-500 text-white' : 'bg-orange-500 text-white'
                    }`}>
                      {matchScore.toFixed(0)}% Match
                      {item.rejection_probability > 30 && (
                        <span className="ml-2 opacity-80">
                          • {item.rejection_probability?.toFixed(0)}% Risk
                        </span>
                      )}
                    </div>
                  )}
                  
                  <div className="p-6">
                    <div className="w-12 h-12 rounded-2xl bg-brand-bg flex items-center justify-center mb-4">
                      <Briefcase className="text-brand-accent" size={24} />
                    </div>
                    
                    <h3 className="font-black text-brand-dark text-lg mb-2 group-hover:text-brand-accent transition-colors">
                      {job?.title || 'Job Title'}
                    </h3>
                    <p className="text-slate-500 font-medium mb-1">🏢 {job?.company || 'Company'}</p>
                    <p className="text-slate-400 text-sm mb-1 flex items-center gap-1">
                      <MapPin size={14} /> {job?.location || 'Location'}
                    </p>

                    {job?.salary && (
                      <p className="text-green-600 font-bold mb-3 flex items-center gap-1">
                        <DollarSign size={16} /> {job.salary}
                      </p>
                    )}

                    {/* Skill Match */}
                    {skillMatch && (
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-1 mb-2">
                          {(skillMatch.matched || []).slice(0, 3).map((skill, i) => (
                            <span key={i} className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-bold flex items-center gap-1">
                              <CheckCircle size={10} /> {skill}
                            </span>
                          ))}
                        </div>
                        {skillMatch.missing?.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {skillMatch.missing.slice(0, 2).map((skill, i) => (
                              <span key={i} className="px-2 py-1 bg-red-100 text-red-600 rounded-lg text-xs font-bold">
                                ✗ {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    <a
                      href={job?.apply_url || job?.url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full flex items-center justify-center gap-2 bg-brand-dark text-white py-3 rounded-xl font-bold uppercase tracking-widest text-sm hover:bg-brand-accent transition-colors"
                    >
                      Apply Now <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {filteredData.length === 0 && !loading && (
          <div className="text-center py-20 bg-white rounded-3xl">
            <Briefcase className="mx-auto text-brand-accent mb-4" size={48} />
            <h3 className="text-2xl font-black text-brand-dark mb-2">No Jobs Found</h3>
            <p className="text-slate-400">Try adjusting your search or filters</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Jobs;
