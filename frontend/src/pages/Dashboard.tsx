import React, { useEffect, useState, useRef } from 'react';
import { StatusCard } from '../components/StatusCard';
import { RiskBadge } from '../components/RiskBadge';
import { DensityChart } from '../components/DensityChart';
import { EventTimeline } from '../components/EventTimeline';
import { VideoPreview } from '../components/VideoPreview';
import { LiveEventFeed } from '../components/LiveEventFeed';
import { Activity, Users, AlertTriangle, UploadCloud, Play, Square, FileVideo, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../api/client';
import { TelemetryFrame, HazardEvent } from '../types';

export const Dashboard: React.FC = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);
  const [videoObjectUrl, setVideoObjectUrl] = useState<string | null>(null);
  
  // Video Analysis State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressPct, setProgressPct] = useState(0);
  const [processedFrames, setProcessedFrames] = useState(0);
  const [totalFrames, setTotalFrames] = useState(100);

  // Telemetry state
  const [telemetryHistory, setTelemetryHistory] = useState<{ frame_id: number; density: number; probability: number }[]>([]);
  const [latestFrame, setLatestFrame] = useState<TelemetryFrame | null>(null);
  const [activeEvents, setActiveEvents] = useState<HazardEvent[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Setup WebSocket connection to /ws/telemetry
  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/ws/telemetry`;

    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.prediction_probability !== undefined || data.density_ped_per_m2 !== undefined) {
            const frame: TelemetryFrame = {
              timestamp: data.timestamp || Date.now() / 1000,
              frame_id: data.frame_id || 0,
              scene_id: data.scene_id || 'LIVE_SCENE',
              zone_id: data.zone_id || 'ZONE_MAIN',
              pedestrian_count: data.pedestrian_count || 0,
              density_ped_per_m2: data.density_ped_per_m2 || 0.0,
              prediction_probability: data.prediction_probability || 0.0,
              risk_level: data.risk_level || 'LOW',
              binary_prediction: data.binary_prediction || 0,
              active_events_count: data.active_events_count || 0,
              active_events: data.active_events || [],
            };

            setLatestFrame(frame);
            if (data.active_events) {
              setActiveEvents(data.active_events);
            }

            if (data.progress_pct !== undefined) {
              setProgressPct(data.progress_pct);
              setProcessedFrames(data.frame_id || 0);
              if (data.total_frames) setTotalFrames(data.total_frames);
            }

            setTelemetryHistory((prev) => [
              ...prev.slice(-25),
              {
                frame_id: frame.frame_id,
                density: frame.density_ped_per_m2,
                probability: frame.prediction_probability,
              },
            ]);
          }
        } catch (e) {}
      };
    } catch (e) {}

    return () => {
      if (ws) ws.close();
    };
  }, []);

  // Poll video progress if analyzing
  useEffect(() => {
    if (!isAnalyzing || !activeSessionId) return;

    const interval = setInterval(async () => {
      try {
        const prog = await apiClient.getAnalysisProgress(activeSessionId);
        if (prog) {
          setProgressPct(prog.progress || 0);
          setProcessedFrames(prog.frames_processed || 0);
          if (prog.total_frames) setTotalFrames(prog.total_frames);

          if (prog.status === 'COMPLETED' || prog.status === 'STOPPED' || prog.status === 'FAILED') {
            setIsAnalyzing(false);
          }
        }
      } catch (e) {}
    }, 500);

    return () => clearInterval(interval);
  }, [isAnalyzing, activeSessionId]);

  const handleFileUpload = async (file: File) => {
    try {
      const res = await apiClient.uploadVideo(file);
      setActiveSessionId(res.session_id);
      setUploadedFilename(file.name);
      setTotalFrames(res.total_frames || 100);
      setVideoObjectUrl(URL.createObjectURL(file));
      setProgressPct(0);
      setProcessedFrames(0);
    } catch (e) {
      alert('Video upload failed. Please try an MP4/AVI/MOV file.');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!activeSessionId) return;
    try {
      await apiClient.startAnalysis(activeSessionId);
      setIsAnalyzing(true);
    } catch (e) {
      alert('Failed to start video analysis.');
    }
  };

  const toggleMonitoring = async () => {
    if (isMonitoring) {
      await apiClient.stopMonitoring();
      setIsMonitoring(false);
    } else {
      await apiClient.startMonitoring();
      setIsMonitoring(true);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Bar */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-bold text-slate-100">Live Crowd Monitoring & Video Analysis Dashboard</h2>
            <RiskBadge riskLevel={latestFrame?.risk_level || 'LOW'} probability={latestFrame?.prediction_probability} />
          </div>
          <p className="text-xs text-slate-400 mt-1">Realtime spatiotemporal bottleneck prediction engine (Y30 horizon)</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={toggleMonitoring}
            className={`px-4 py-2 rounded-lg font-semibold text-xs flex items-center space-x-2 transition-all shadow-lg ${
              isMonitoring
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
            }`}
          >
            {isMonitoring ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isMonitoring ? 'Stop Live Monitoring' : 'Start Live Monitoring'}</span>
          </button>
        </div>
      </div>

      {/* Video Upload & Analysis Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Upload Card */}
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200">Video File Analysis</h3>
            {uploadedFilename && (
              <span className="text-xs bg-emerald-950/60 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>LOADED</span>
              </span>
            )}
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
            accept=".mp4,.avi,.mov,.mkv"
            className="hidden"
          />

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl p-6 text-center cursor-pointer transition-all bg-slate-900/40 hover:bg-slate-900/80 space-y-2"
          >
            <UploadCloud className="w-8 h-8 mx-auto text-sky-400 opacity-80" />
            <p className="text-xs font-semibold text-slate-300">
              {uploadedFilename ? uploadedFilename : 'Drag & Drop Video or Click to Browse'}
            </p>
            <p className="text-[10px] text-slate-500">Supports .MP4, .AVI, .MOV, .MKV</p>
          </div>

          {activeSessionId && (
            <div className="space-y-3 pt-2">
              <button
                onClick={startAnalysis}
                disabled={isAnalyzing}
                className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-600/20 disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>{isAnalyzing ? 'Analyzing Video Frames...' : 'Start BHID Video Analysis'}</span>
              </button>

              {/* Progress Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Frame: {processedFrames} / {totalFrames}</span>
                  <span>{progressPct.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-sky-500 to-indigo-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progressPct}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Video Preview */}
        <div className="md:col-span-2">
          <VideoPreview
            videoUrl={videoObjectUrl}
            filename={uploadedFilename || undefined}
            isProcessing={isAnalyzing}
            progressPct={progressPct}
          />
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatusCard
          title="Crowd Density"
          value={`${latestFrame?.density_ped_per_m2 || '0.00'} ped/m²`}
          subtitle="Spatial ROI Threshold: 3.5 ped/m²"
          icon={<Activity className="w-5 h-5" />}
        />

        <StatusCard
          title="Pedestrian Count"
          value={latestFrame?.pedestrian_count || 0}
          subtitle="Active tracked pedestrians"
          icon={<Users className="w-5 h-5" />}
        />

        <StatusCard
          title="Hazard Probability"
          value={`${((latestFrame?.prediction_probability || 0.0) * 100).toFixed(1)}%`}
          subtitle="Target Horizon Y30 (30s ahead)"
          icon={<AlertTriangle className="w-5 h-5" />}
        />

        <StatusCard
          title="Active Hazards"
          value={activeEvents.length}
          subtitle="Zone Duplicate Locks Active"
          icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Main Charts & Live Feed Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <DensityChart data={telemetryHistory} />
        </div>
        <div className="space-y-6">
          <LiveEventFeed events={activeEvents} />
          <EventTimeline events={activeEvents} />
        </div>
      </div>
    </div>
  );
};
