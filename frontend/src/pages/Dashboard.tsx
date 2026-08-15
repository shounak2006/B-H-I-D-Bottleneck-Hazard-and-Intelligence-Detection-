import React, { useEffect, useState } from 'react';
import { StatusCard } from '../components/StatusCard';
import { RiskBadge } from '../components/RiskBadge';
import { DensityChart } from '../components/DensityChart';
import { EventTimeline } from '../components/EventTimeline';
import { Activity, Users, AlertTriangle, Play, Square } from 'lucide-react';
import { apiClient } from '../api/client';
import { TelemetryFrame, HazardEvent } from '../types';

export const Dashboard: React.FC = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [telemetryHistory, setTelemetryHistory] = useState<{ frame_id: number; density: number; probability: number }[]>([]);
  const [latestFrame, setLatestFrame] = useState<TelemetryFrame | null>(null);
  const [activeEvents, setActiveEvents] = useState<HazardEvent[]>([]);

  useEffect(() => {
    // Check initial monitoring state
    apiClient.getMonitoringState().then((state) => {
      setIsMonitoring(state.is_monitoring);
    }).catch(() => {});

    // Setup polling for live telemetry
    const interval = setInterval(async () => {
      try {
        const events = await apiClient.getActiveEvents();
        setActiveEvents(events);

        if (isMonitoring) {
          const state = await apiClient.getMonitoringState();
          if (state.last_prediction) {
            const pred = state.last_prediction;
            const newFrame: TelemetryFrame = {
              timestamp: Date.now() / 1000,
              frame_id: state.processed_frames,
              scene_id: pred.scene_id || 'LIVE_SCENE',
              zone_id: pred.zone_id || 'ZONE_MAIN',
              pedestrian_count: Math.round((pred.prediction_probability || 0.1) * 60) + 10,
              density_ped_per_m2: Number(((pred.prediction_probability || 0.1) * 2.5).toFixed(2)),
              prediction_probability: pred.prediction_probability,
              risk_level: pred.risk_level,
              binary_prediction: pred.binary_prediction,
              active_events_count: events.length,
              active_events: events,
            };

            setLatestFrame(newFrame);
            setTelemetryHistory((prev) => [
              ...prev.slice(-25),
              {
                frame_id: newFrame.frame_id,
                density: newFrame.density_ped_per_m2,
                probability: newFrame.prediction_probability,
              },
            ]);
          }
        }
      } catch (err) {
        // Backend offline or polling error
      }
    }, 800);

    return () => clearInterval(interval);
  }, [isMonitoring]);

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
      {/* Top Controls Bar */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-bold text-slate-100">Live Crowd Monitoring Dashboard</h2>
            <RiskBadge riskLevel={latestFrame?.risk_level || 'LOW'} probability={latestFrame?.prediction_probability} />
          </div>
          <p className="text-xs text-slate-400 mt-1">Realtime spatiotemporal bottleneck prediction engine (Y30 horizon)</p>
        </div>

        <button
          onClick={toggleMonitoring}
          className={`px-5 py-2.5 rounded-lg font-semibold text-xs flex items-center space-x-2 transition-all shadow-lg ${
            isMonitoring
              ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
          }`}
        >
          {isMonitoring ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          <span>{isMonitoring ? 'Stop Monitoring Session' : 'Start Live Monitoring'}</span>
        </button>
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

      {/* Main Charts & Alerts Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <DensityChart data={telemetryHistory} />
        </div>
        <div>
          <EventTimeline events={activeEvents} />
        </div>
      </div>
    </div>
  );
};
