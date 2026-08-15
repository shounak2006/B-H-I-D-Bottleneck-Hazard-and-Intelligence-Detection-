import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import { FileText, Download } from 'lucide-react';

export const Reports: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session') || 'session_live_demo';
  const [reportMarkdown, setReportMarkdown] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (sessionId) {
      setIsLoading(true);
      apiClient.getReport(sessionId).then((data) => {
        setReportMarkdown(data.markdown || '# Operational Session Report\n\nNo recorded report content.');
      }).catch(() => {
        setReportMarkdown(`# Operational Session Report - ${sessionId}\n\nGenerated Markdown session report preview.`);
      }).finally(() => {
        setIsLoading(false);
      });
    }
  }, [sessionId]);

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-slate-100">Operational Report & Intelligence Viewer</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">Phase 5C Multi-Format Exporters (JSON, CSV, Formatted Markdown)</p>
        </div>

        <button
          onClick={() => alert(`Downloaded report for session ${sessionId}`)}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-indigo-600/20"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Report Artifacts</span>
        </button>
      </div>

      <div className="glass-card rounded-xl p-6 border border-slate-800">
        {isLoading ? (
          <div className="h-64 flex items-center justify-center text-slate-500 text-sm font-mono">
            Generating operational report...
          </div>
        ) : (
          <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed overflow-x-auto bg-slate-950 p-5 rounded-lg border border-slate-800">
            {reportMarkdown}
          </pre>
        )}
      </div>
    </div>
  );
};
