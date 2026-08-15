import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ReplayPlayer } from '../components/ReplayPlayer';
import { apiClient } from '../api/client';
import { PlayCircle } from 'lucide-react';

export const ReplayViewer: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session') || 'session_live_demo';
  const [totalFrames, setTotalFrames] = useState(100);

  useEffect(() => {
    if (sessionId) {
      apiClient.getReplaySession(sessionId).then((data) => {
        if (data.total_frames) {
          setTotalFrames(data.total_frames);
        }
      }).catch(() => {});
    }
  }, [sessionId]);

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <PlayCircle className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-slate-100">Deterministic Historical Replay Engine</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">Phase 5B offline replay reconstructing session telemetry without model re-inference</p>
        </div>
      </div>

      <ReplayPlayer
        sessionId={sessionId}
        totalFrames={totalFrames}
        onPlay={() => apiClient.playReplay(sessionId)}
      />
    </div>
  );
};
