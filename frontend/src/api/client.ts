import axios from 'axios';
import { HealthStatus, SessionInfo, ValidationResult, HazardEvent } from '../types';

const API_BASE = '/api';

export const apiClient = {
  getHealth: async (): Promise<HealthStatus> => {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  startMonitoring: async (sceneId = 'LIVE_SCENE', zoneId = 'ZONE_MAIN') => {
    const res = await axios.post(`${API_BASE}/monitoring/start`, { scene_id: sceneId, zone_id: zoneId });
    return res.data;
  },

  stopMonitoring: async () => {
    const res = await axios.post(`${API_BASE}/monitoring/stop`);
    return res.data;
  },

  getMonitoringState: async () => {
    const res = await axios.get(`${API_BASE}/monitoring/state`);
    return res.data;
  },

  getActiveEvents: async (): Promise<HazardEvent[]> => {
    const res = await axios.get(`${API_BASE}/events/active`);
    return res.data.active_events || [];
  },

  getSessions: async (): Promise<SessionInfo[]> => {
    const res = await axios.get(`${API_BASE}/sessions`);
    return res.data.sessions || [];
  },

  getReplaySession: async (sessionId: string) => {
    const res = await axios.get(`${API_BASE}/replay/${sessionId}`);
    return res.data;
  },

  playReplay: async (sessionId: string) => {
    const res = await axios.post(`${API_BASE}/replay/${sessionId}/play`);
    return res.data;
  },

  getReport: async (sessionId: string) => {
    const res = await axios.get(`${API_BASE}/reports/${sessionId}`);
    return res.data;
  },

  runValidation: async (sessionId = 'default_session'): Promise<ValidationResult> => {
    const res = await axios.post(`${API_BASE}/validation/run`, { session_id: sessionId });
    return res.data.evaluation;
  },
};
