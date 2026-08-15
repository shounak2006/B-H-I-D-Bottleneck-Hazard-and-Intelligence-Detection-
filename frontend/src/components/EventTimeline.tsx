import React from 'react';
import { HazardEvent } from '../types';
import { AlertTriangle, ShieldAlert } from 'lucide-react';
import { RiskBadge } from './RiskBadge';

interface EventTimelineProps {
  events: HazardEvent[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="glass-card rounded-xl p-5 text-center text-slate-400 text-sm border border-slate-800">
        <ShieldAlert className="w-8 h-8 mx-auto text-emerald-400 mb-2 opacity-60" />
        <p className="font-semibold text-slate-300">No Active Bottleneck Hazards</p>
        <p className="text-xs text-slate-500 mt-1">Spatial zones operating within normal density limits.</p>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h3 className="font-bold text-sm text-slate-200">Active Bottleneck Hazard Alerts</h3>
        </div>
        <span className="text-xs bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded font-mono border border-rose-500/30">
          {events.length} ACTIVE
        </span>
      </div>

      <div className="space-y-2">
        {events.map((evt) => (
          <div key={evt.event_id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs text-slate-300 font-bold">{evt.scene_id} / {evt.zone_id}</span>
                <RiskBadge riskLevel={evt.risk_level} probability={evt.prediction_probability} />
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Event ID: <span className="font-mono text-slate-300">{evt.event_id}</span> | Escalations: {evt.escalation_count}
              </p>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-amber-950/40 px-2 py-1 rounded border border-amber-800">
              {evt.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
