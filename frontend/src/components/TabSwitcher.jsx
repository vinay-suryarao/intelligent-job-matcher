import React from 'react';

const TabSwitcher = ({ tabs, activeTab, onChange, className = '' }) => {
  return (
    <div className={`flex bg-white/5 backdrop-blur-lg rounded-xl p-1 border border-white/10 ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id || tab.value || tab}
          onClick={() => onChange(tab.id || tab.value || tab)}
          className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
            (tab.id || tab.value || tab) === activeTab
              ? 'bg-blue-600 text-white shadow-lg'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <div className="flex items-center justify-center gap-2">
            {tab.icon && <span>{tab.icon}</span>}
            <span>{tab.label || tab.name || tab}</span>
            {tab.count !== undefined && (
              <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${
                (tab.id || tab.value || tab) === activeTab
                  ? 'bg-white/20'
                  : 'bg-white/10'
              }`}>
                {tab.count}
              </span>
            )}
          </div>
        </button>
      ))}
    </div>
  );
};

// Alternative pill-style tabs
export const PillTabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {tabs.map((tab) => (
        <button
          key={tab.id || tab.value || tab}
          onClick={() => onChange(tab.id || tab.value || tab)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
            (tab.id || tab.value || tab) === activeTab
              ? 'bg-blue-600 text-white'
              : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
          }`}
        >
          {tab.label || tab.name || tab}
        </button>
      ))}
    </div>
  );
};

// Underline-style tabs
export const UnderlineTabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="flex border-b border-white/10">
      {tabs.map((tab) => (
        <button
          key={tab.id || tab.value || tab}
          onClick={() => onChange(tab.id || tab.value || tab)}
          className={`px-6 py-3 text-sm font-medium transition-all duration-200 relative ${
            (tab.id || tab.value || tab) === activeTab
              ? 'text-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          {tab.label || tab.name || tab}
          {(tab.id || tab.value || tab) === activeTab && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
          )}
        </button>
      ))}
    </div>
  );
};

export default TabSwitcher;
