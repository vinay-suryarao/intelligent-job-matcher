import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import api from '../services/api';
import { Search, Filter, ExternalLink, GraduationCap, MapPin, Clock, DollarSign, MessageCircle } from 'lucide-react';

const Internships = () => {
  const [internships, setInternships] = useState([]);
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
        const data = await api.getInternshipMatches(50);
        if (data.matches) setMatches(data.matches);
      } else {
        const data = await api.getInternships(100);
        if (data.internships) setInternships(data.internships);
      }
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const displayData = viewMode === 'matches' ? matches : internships;
  
  const filteredData = displayData.filter(item => {
    const internship = viewMode === 'matches' ? item.internship || item.job : item;
    const matchesSearch = !searchTerm || 
      internship?.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      internship?.company?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !locationFilter || 
      internship?.location?.toLowerCase().includes(locationFilter.toLowerCase());
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
            <h1 className="text-5xl font-black text-brand-dark tracking-tighter uppercase mb-2">Internships</h1>
            <p className="text-slate-400 font-medium text-lg">Find your perfect internship opportunity</p>
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
            📋 All Internships
          </button>
        </div>

        {/* Search & Filter */}
        <div className="flex gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search internships..."
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
              const internship = viewMode === 'matches' ? item.internship || item.job : item;
              const matchScore = item.match_score;

              return (
                <div key={internship?.id || index} className="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100 hover:border-brand-accent transition-all group">
                  {matchScore && (
                    <div className={`p-3 text-center font-black text-sm uppercase tracking-widest ${
                      matchScore >= 80 ? 'bg-green-500 text-white' :
                      matchScore >= 60 ? 'bg-yellow-500 text-white' : 'bg-orange-500 text-white'
                    }`}>
                      {matchScore.toFixed(0)}% Match
                    </div>
                  )}
                  
                  <div className="p-6">
                    <div className="w-12 h-12 rounded-2xl bg-brand-bg flex items-center justify-center mb-4">
                      <GraduationCap className="text-brand-accent" size={24} />
                    </div>
                    
                    <h3 className="font-black text-brand-dark text-lg mb-2 group-hover:text-brand-accent transition-colors">
                      {internship?.title || 'Internship'}
                    </h3>
                    <p className="text-slate-500 font-medium mb-1">🏢 {internship?.company || 'Company'}</p>
                    <p className="text-slate-400 text-sm mb-1 flex items-center gap-1">
                      <MapPin size={14} /> {internship?.location || 'Location'}
                    </p>
                    {internship?.duration && (
                      <p className="text-slate-400 text-sm mb-3 flex items-center gap-1">
                        <Clock size={14} /> {internship.duration}
                      </p>
                    )}

                    {internship?.stipend && (
                      <p className="text-green-600 font-bold mb-4 flex items-center gap-1">
                        <DollarSign size={16} /> {internship.stipend}
                      </p>
                    )}

                    <a
                      href={internship?.apply_url || internship?.url || internship?.link || internship?.application_link || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => {
                        const url = internship?.apply_url || internship?.url || internship?.link || internship?.application_link;
                        if (!url || url === '#') {
                          e.preventDefault();
                          alert('Application link not available for this internship');
                        }
                      }}
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
            <GraduationCap className="mx-auto text-brand-accent mb-4" size={48} />
            <h3 className="text-2xl font-black text-brand-dark mb-2">No Internships Found</h3>
            <p className="text-slate-400">Try adjusting your search or filters</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Internships;
