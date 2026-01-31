import React from 'react';
import { 
  LayoutDashboard, 
  Briefcase, 
  Settings, 
  BrainCircuit, 
  ChevronRight,
  LogOut,
  BarChart3,
  GraduationCap,
  ClipboardCheck
} from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const menuItems = [
    { icon: <LayoutDashboard size={20} />, label: 'Dashboard', path: '/dashboard' },
    { icon: <Briefcase size={20} />, label: 'Jobs', path: '/jobs' },
    { icon: <GraduationCap size={20} />, label: 'Internships', path: '/internships' },
    { icon: <ClipboardCheck size={20} />, label: 'Review & Result', path: '/review' },
    { icon: <BarChart3 size={20} />, label: 'Statistics', path: '/statistics' },
    { icon: <Settings size={20} />, label: 'Settings', path: '/settings' },
  ];

  const handleLogout = (e) => {
    e.preventDefault();
    logout();
    navigate('/'); // Redirect to home page after logout
  };

  return (
    <aside className="w-64 h-screen bg-white border-r border-slate-200 flex flex-col fixed left-0 top-0 pt-8 shadow-sm z-40">
      {/* Logo Section */}
      <div className="px-8 flex items-center gap-3 mb-10 group cursor-pointer" onClick={() => navigate('/dashboard')}>
        <div className="bg-brand-dark p-2 rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-300">
          <BrainCircuit className="text-white w-6 h-6" />
        </div>
        <span className="text-2xl font-black text-brand-dark tracking-tighter uppercase">HireStorm</span>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-4 space-y-2">
        {menuItems.map((item, idx) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={idx}
              to={item.path}
              className={`w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all duration-300 font-bold text-sm uppercase tracking-widest ${
                isActive 
                  ? 'bg-brand-dark text-white shadow-xl shadow-brand-dark/20' 
                  : 'text-slate-400 hover:bg-brand-bg hover:text-brand-dark'
              }`}
            >
              <span className={isActive ? 'text-brand-accent' : ''}>
                {item.icon}
              </span>
              <span>{item.label}</span>
              
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_10px_#FF9F56]"></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Profile Card -> Handles Logout & Redirects to Home */}
      <div 
        onClick={handleLogout}
        className="p-6 border-t border-slate-100 block group cursor-pointer"
      >
        <div className="flex items-center gap-3 p-3 rounded-2xl bg-brand-bg/50 group-hover:bg-red-50 transition-all">
          <div className="w-10 h-10 rounded-xl bg-brand-dark flex items-center justify-center text-white font-black group-hover:bg-red-500 transition-colors duration-300 shadow-sm">
            <LogOut size={18} className="group-hover:rotate-12 transition-transform" />
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-xs font-black text-brand-dark uppercase tracking-tight group-hover:hidden truncate">
              {user?.full_name || 'User'}
            </p>
            <p className="text-xs font-black text-red-500 uppercase tracking-tight hidden group-hover:block">
              Logout
            </p>
          </div>
          <div className="ml-auto text-slate-300 group-hover:text-red-500 transition-colors">
             <ChevronRight size={14} />
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;