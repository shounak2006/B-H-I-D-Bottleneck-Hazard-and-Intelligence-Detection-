import React, { useState } from 'react';
import { Play, Pause, RotateCcw, FastForward } from 'lucide-react';

interface ReplayPlayerProps {
  sessionId: string;
  totalFrames: number;
  onPlay?: () => void;
  onPause?: () => void;
}

export const ReplayPlayer: React.FC<ReplayPlayerProps> = ({ sessionId, totalFrames, onPlay, onPause }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);

  const togglePlay = () => {
    if (isPlaying) {
      setIsPlaying(false);
      if (onPause) onPause();
    } else {
      setIsPlaying(true);
      if (onPlay) onPlay();
    }
  };

  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-200">Historical Replay Controller</h3>
          <p className="text-xs text-slate-400 font-mono">Session ID: {sessionId}</p>
        </div>
        <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded font-mono border border-indigo-500/30">
          [REPLAY MODE]
        </span>
      </div>

      {/* Frame canvas mockup */}
      <div className="h-64 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center relative overflow-hidden">
        <div className="text-center text-slate-500 space-y-1">
          <p className="text-xs font-mono text-slate-400">Rendered Visual Telemetry Overlay</p>
          <p className="text-[10px] text-slate-600">Frame {currentFrame} / {totalFrames}</p>
        </div>
        <div className="absolute bottom-2 right-2 bg-rose-950/80 text-rose-300 text-[10px] font-mono px-2 py-0.5 rounded border border-rose-800">
          [REPLAY MODE]
        </div>
      </div>

      {/* Timeline Controls */}
      <div className="space-y-2">
        <input
          type="range"
          min={0}
          max={totalFrames || 100}
          value={currentFrame}
          onChange={(e) => setCurrentFrame(Number(e.target.value))}
          className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
        />

        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentFrame(0)}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center space-x-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
            <button
              onClick={togglePlay}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1 shadow-md shadow-indigo-600/20"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
          </div>

          <div className="text-xs font-mono text-slate-400">
            Frame: <span className="text-slate-200 font-bold">{currentFrame}</span> / {totalFrames}
          </div>
        </div>
      </div>
    </div>
  );
};
