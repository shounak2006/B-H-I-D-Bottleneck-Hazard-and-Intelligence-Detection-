import React from 'react';
import { SessionInfo } from '../types';
import { Database, Play, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SessionTableProps {
  sessions: SessionInfo[];
}

export const SessionTable: React.FC<SessionTableProps> = ({ sessions }) => {
  const navigate = useNavigate();

  if (!sessions || sessions.length === 0) {
    return (
      <div className="glass-card rounded-xl p-8 text-center text-slate-400 text-sm border border-slate-800">
        <Database className="w-10 h-10 mx-auto text-slate-600 mb-3" />
        <p className="font-semibold text-slate-300">No Recorded Operational Sessions Found</p>
        <p className="text-xs text-slate-500 mt-1">Start live monitoring from the Dashboard to record sessions.</p>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl overflow-hidden border border-slate-800">
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase border-b border-slate-800">
          <tr>
            <th className="p-4">Session ID</th>
            <th className="p-4">Scene / Zone</th>
            <th className="p-4">Total Frames</th>
            <th className="p-4">Created At</th>
            <th className="p-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-mono">
          {sessions.map((s) => (
            <tr key={s.session_id} className="hover:bg-slate-800/40 transition-colors">
              <td className="p-4 font-bold text-sky-400">{s.session_id}</td>
              <td className="p-4 text-slate-300">{s.active_scene || 'DEFAULT'} / {s.active_zone || 'MAIN'}</td>
              <td className="p-4 text-slate-300">{s.total_frames || 0}</td>
              <td className="p-4 text-slate-400">{s.created_at || 'Just Now'}</td>
              <td className="p-4 text-right space-x-2">
                <button
                  onClick={() => navigate(`/replay?session=${s.session_id}`)}
                  className="px-3 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 transition-all text-xs font-semibold inline-flex items-center space-x-1"
                >
                  <Play className="w-3 h-3" />
                  <span>Replay</span>
                </button>
                <button
                  onClick={() => navigate(`/reports?session=${s.session_id}`)}
                  className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all text-xs font-semibold inline-flex items-center space-x-1"
                >
                  <FileText className="w-3 h-3" />
                  <span>Report</span>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
