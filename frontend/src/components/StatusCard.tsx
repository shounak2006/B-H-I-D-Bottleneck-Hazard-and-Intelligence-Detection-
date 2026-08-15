import React from 'react';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({ title, value, subtitle, icon, trend }) => {
  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">{title}</span>
        <div className="p-2 rounded-lg bg-slate-800/80 text-sky-400">{icon}</div>
      </div>
      <div className="mt-4">
        <div className="text-2xl font-bold text-slate-100 tracking-tight font-mono">{value}</div>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        {trend && <p className="text-xs text-emerald-400 mt-1 font-medium">{trend}</p>}
      </div>
    </div>
  );
};
