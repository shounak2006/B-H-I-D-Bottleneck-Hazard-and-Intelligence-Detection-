import React from 'react';

interface TelemetryPoint {
  frame_id: number;
  density: number;
  probability: number;
}

interface DensityChartProps {
  data: TelemetryPoint[];
}

export const DensityChart: React.FC<DensityChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-500 text-sm font-mono border border-dashed border-slate-800 rounded-xl">
        Awaiting live telemetry stream...
      </div>
    );
  }

  const maxDensity = Math.max(...data.map(d => d.density), 3.0);
  const points = data.slice(-20);

  return (
    <div className="glass-card rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-200">Realtime Crowd Density & Risk Trend</h3>
          <p className="text-xs text-slate-400">Live 2.5Hz spatiotemporal density stream (ped/m²)</p>
        </div>
        <span className="text-xs font-mono text-sky-400 bg-sky-950/50 px-2 py-1 rounded border border-sky-800">
          Last: {points[points.length - 1]?.density.toFixed(2)} ped/m²
        </span>
      </div>

      {/* SVG Stream Chart */}
      <div className="h-44 w-full relative flex items-end space-x-1 pt-4 pb-2 border-b border-slate-800">
        {points.map((p, idx) => {
          const heightPct = Math.min(100, Math.max(10, (p.density / maxDensity) * 100));
          const isHighRisk = p.probability >= 0.60;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center group relative h-full justify-end">
              <div
                className={`w-full rounded-t transition-all duration-300 ${
                  isHighRisk ? 'bg-rose-500 shadow-lg shadow-rose-500/30' : 'bg-indigo-500/70 hover:bg-sky-400'
                }`}
                style={{ height: `${heightPct}%` }}
              ></div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-between items-center text-[10px] text-slate-500 font-mono mt-2">
        <span>T - {points.length * 0.4}s</span>
        <span>LIVE STREAM</span>
        <span>NOW</span>
      </div>
    </div>
  );
};
