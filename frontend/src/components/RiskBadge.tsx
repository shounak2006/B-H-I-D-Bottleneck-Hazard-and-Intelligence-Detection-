import React from 'react';

interface RiskBadgeProps {
  riskLevel: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | string;
  probability?: number;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ riskLevel, probability }) => {
  const getBadgeClass = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'risk-low';
      case 'MODERATE':
        return 'risk-moderate';
      case 'HIGH':
        return 'risk-high';
      case 'CRITICAL':
        return 'risk-critical';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border text-xs font-bold font-mono uppercase shadow-sm ${getBadgeClass(riskLevel)}`}>
      <span className="w-2 h-2 rounded-full bg-current"></span>
      <span>{riskLevel}</span>
      {probability !== undefined && (
        <span className="opacity-80 border-l border-current/30 pl-2">
          {(probability * 100).toFixed(1)}%
        </span>
      )}
    </div>
  );
};
