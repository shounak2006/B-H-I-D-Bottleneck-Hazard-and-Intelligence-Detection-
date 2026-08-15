export interface HealthStatus {
  status: string;
  system: string;
  version: string;
}

export interface TelemetryFrame {
  timestamp: number;
  frame_id: number;
  scene_id: string;
  zone_id: string;
  pedestrian_count: number;
  density_ped_per_m2: number;
  prediction_probability: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  binary_prediction: number;
  active_events_count: number;
  active_events: HazardEvent[];
}

export interface HazardEvent {
  event_id: string;
  scene_id: string;
  zone_id: string;
  risk_level: string;
  status: 'ACTIVE' | 'ESCALATED' | 'RESOLVED';
  prediction_probability: number;
  start_timestamp: number;
  last_updated_timestamp: number;
  resolution_timestamp?: number;
  escalation_count: number;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  start_timestamp: number;
  total_frames: number;
  active_scene: string;
  active_zone: string;
}

export interface ValidationResult {
  overall_status: 'PASSED' | 'WARNING' | 'FAILED';
  readiness_score_pct: number;
  component_scores: Record<string, number>;
  details: Record<string, any>;
}
