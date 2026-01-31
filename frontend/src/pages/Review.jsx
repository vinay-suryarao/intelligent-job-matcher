import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import MatchHistoryTable from '../components/MatchHistoryTable';
import MatchList from '../components/MatchList';
import { ClipboardCheck, History, MessageCircle } from 'lucide-react';

const Review = () => {
  const [activeTab, setActiveTab] = useState('review');
  const [showChat, setShowChat] = useState(false);

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
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-5xl font-black text-brand-dark tracking-tighter uppercase mb-2">
            Review & Results
          </h1>
          <p className="text-slate-400 font-medium text-lg">
            Track your applications and discover perfect job matches
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="bg-white rounded-3xl p-2 mb-8 inline-flex gap-2 shadow-sm border border-slate-200">
          <button
            onClick={() => setActiveTab('review')}
            className={`px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest transition-all flex items-center gap-3 ${
              activeTab === 'review'
                ? 'bg-brand-dark text-white shadow-lg'
                : 'text-slate-400 hover:text-brand-dark'
            }`}
          >
            <History size={18} />
            Review History
          </button>
          <button
            onClick={() => setActiveTab('results')}
            className={`px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest transition-all flex items-center gap-3 ${
              activeTab === 'results'
                ? 'bg-brand-dark text-white shadow-lg'
                : 'text-slate-400 hover:text-brand-dark'
            }`}
          >
            <ClipboardCheck size={18} />
            Match Results
          </button>
        </div>

        {/* Content Area */}
        <div className="animate-in fade-in duration-300">
          {activeTab === 'review' ? (
            <MatchHistoryTable />
          ) : (
            <MatchList />
          )}
        </div>
      </main>
    </div>
  );
};

export default Review;