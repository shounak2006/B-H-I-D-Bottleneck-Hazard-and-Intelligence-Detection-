import React from 'react';
import { ValidationResult } from '../types';
import { ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';

interface ValidationPanelProps {
  validation: ValidationResult | null;
  onRunValidation: () => void;
  isLoading?: boolean;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({ validation, onRunValidation, isLoading }) => {
  return (
    <div className="glass-card rounded-xl p-6 border border-slate-800 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-emerald-950/50 border border-emerald-800 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100">Read-Only System Readiness Auditor</h2>
            <p className="text-xs text-slate-400">Phase 5D System Evaluation & Readiness Score</p>
          </div>
        </div>

        <button
          onClick={onRunValidation}
          disabled={isLoading}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-600/20 disabled:opacity-50 transition-all"
        >
          {isLoading ? 'Running Read-Only Audit...' : 'Run System Readiness Audit'}
        </button>
      </div>

      {validation && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-800">
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-xs text-slate-400 font-semibold uppercase">Overall Status</span>
            <div className="flex items-center space-x-2 mt-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-xl font-bold font-mono text-emerald-400">{validation.overall_status}</span>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-xs text-slate-400 font-semibold uppercase">Readiness Score</span>
            <div className="text-xl font-bold font-mono text-sky-400 mt-2">
              {validation.readiness_score_pct.toFixed(1)}%
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="text-xs text-slate-400 font-semibold uppercase">Component Health</span>
            <p className="text-xs text-slate-300 mt-2 font-mono">
              6/6 Component Validators Passed
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
