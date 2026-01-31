import React from 'react';
import { Search, Bell, ArrowUpRight } from 'lucide-react';

const Navbar = () => {
  return (
    <nav className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-50 flex items-center justify-between px-10 fixed top-0 right-0 left-64 z-10">
      <div className="relative w-96">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
        <input 
          type="text" 
          placeholder="Kaunsi job chahiye?..." 
          className="w-full bg-slate-50 border-none rounded-2xl py-3 pl-12 pr-4 text-sm focus:ring-2 focus:ring-indigo-500 transition-all outline-none"
        />
      </div>

      <div className="flex items-center gap-6">
        <button className="p-2.5 rounded-xl bg-slate-50 text-slate-500 hover:bg-slate-100 relative">
          <Bell size={20} />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
        </button>
        <button className="bg-slate-900 text-white px-6 py-3 rounded-2xl font-bold flex items-center gap-2 hover:bg-slate-800 transition-all shadow-lg shadow-slate-200 text-sm">
          Direct Match <ArrowUpRight size={16} />
        </button>
      </div>
    </nav>
  );
};

export default Navbar;