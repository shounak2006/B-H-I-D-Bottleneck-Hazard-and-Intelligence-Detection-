import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, Database, PlayCircle, FileText, ShieldCheck } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <nav className="glass-panel sticky top-0 z-50 px-6 py-3 flex items-center justify-between border-b border-slate-800">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20">
          B
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-wide gradient-text">BHID v1.0</h1>
          <p className="text-xs text-slate-400 font-mono">Bottleneck Hazard & Intelligence Detection</p>
        </div>
      </div>

      <div className="flex space-x-1">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive
                ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <Activity className="w-4 h-4" />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/sessions"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive
                ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <Database className="w-4 h-4" />
          <span>Sessions</span>
        </NavLink>

        <NavLink
          to="/replay"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive
                ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <PlayCircle className="w-4 h-4" />
          <span>Replay</span>
        </NavLink>

        <NavLink
          to="/reports"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive
                ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <FileText className="w-4 h-4" />
          <span>Reports</span>
        </NavLink>

        <NavLink
          to="/validation"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive
                ? 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Validation</span>
        </NavLink>
      </div>

      <div className="flex items-center space-x-2">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span className="text-xs text-slate-300 font-mono">LOCALHOST:8000</span>
      </div>
    </nav>
  );
};
