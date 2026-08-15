import React from 'react';
import { Video, Film, CheckCircle2 } from 'lucide-react';

interface VideoPreviewProps {
  videoUrl?: string | null;
  filename?: string;
  isProcessing?: boolean;
  progressPct?: number;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ videoUrl, filename, isProcessing, progressPct }) => {
  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Film className="w-5 h-5 text-sky-400" />
          <h3 className="text-sm font-bold text-slate-200">Video Source Preview</h3>
        </div>
        {filename && (
          <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 truncate max-w-[200px]">
            {filename}
          </span>
        )}
      </div>

      <div className="h-48 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center relative overflow-hidden">
        {videoUrl ? (
          <video src={videoUrl} controls className="w-full h-full object-contain rounded-lg" />
        ) : (
          <div className="text-center text-slate-500 space-y-2">
            <Video className="w-10 h-10 mx-auto text-slate-600 opacity-60" />
            <p className="text-xs font-mono text-slate-400">
              {isProcessing ? 'Processing Video Frames...' : 'No Video Loaded'}
            </p>
            <p className="text-[10px] text-slate-600">Supports MP4, AVI, MOV, MKV files</p>
          </div>
        )}

        {isProcessing && (
          <div className="absolute top-2 right-2 bg-sky-950/90 text-sky-300 text-[10px] font-mono px-2.5 py-1 rounded border border-sky-800 flex items-center space-x-1.5 shadow-lg">
            <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
            <span>ANALYZING ({progressPct?.toFixed(1)}%)</span>
          </div>
        )}
      </div>
    </div>
  );
};
