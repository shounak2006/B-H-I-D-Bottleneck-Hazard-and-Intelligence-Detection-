import React from 'react';
import { AlertOctagon, CheckCircle2, ShieldAlert, TrendingUp } from 'lucide-react';
import { HazardEvent } from '../types';

interface LiveEventFeedProps {
  events: HazardEvent[];
}

export const LiveEventFeed: React.FC<LiveEventFeedProps> = ({ events }) => {
  const formatTime = (ts?: number) => {
    if (!ts) return new Date().toLocaleTimeString();
    return new Date(ts * 1000).toLocaleTimeString();
  };

  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-indigo-400" />
          <h3 className="font-bold text-sm text-slate-200">Realtime Hazard Intelligence Stream</h3>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800">
          LIVE FEED
        </span>
      </div>

      <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs font-mono">
            [SYS_OK] No hazard events recorded in current window.
          </div>
        ) : (
          events.map((evt, idx) => (
            <div
              key={evt.event_id || idx}
              className={`p-2.5 rounded-lg border text-xs font-mono flex items-center justify-between transition-all ${
                evt.risk_level === 'CRITICAL' || evt.risk_level === 'HIGH'
                  ? 'bg-rose-950/40 border-rose-800 text-rose-300'
                  : evt.status === 'ESCALATED'
                  ? 'bg-amber-950/40 border-amber-800 text-amber-300'
                  : 'bg-slate-900 border-slate-800 text-slate-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <span className="opacity-60 text-[10px]">[{formatTime(evt.last_updated_timestamp)}]</span>
                <span className="font-bold">
                  {evt.risk_level} HAZARD {evt.status === 'ESCALATED' ? 'ESCALATED' : 'DETECTED'}
                </span>
              </div>
              <span className="text-[10px] opacity-80 border-l border-current/30 pl-2">
                p={(evt.prediction_probability * 100).toFixed(0)}%
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
