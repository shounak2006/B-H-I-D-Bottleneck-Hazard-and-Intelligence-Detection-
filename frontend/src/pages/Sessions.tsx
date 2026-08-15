import React, { useEffect, useState } from 'react';
import { SessionTable } from '../components/SessionTable';
import { apiClient } from '../api/client';
import { SessionInfo } from '../types';
import { Database, RefreshCw } from 'lucide-react';

export const Sessions: React.FC = () => {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSessions = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getSessions();
      setSessions(data);
    } catch (err) {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-slate-100">Operational Session Registry</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">Recorded operational sessions stored in non-blocking Phase 5A persistence store</p>
        </div>

        <button
          onClick={fetchSessions}
          disabled={isLoading}
          className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center space-x-2 transition-all border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <SessionTable sessions={sessions} />
    </div>
  );
};
