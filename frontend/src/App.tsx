import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { Sessions } from './pages/Sessions';
import { ReplayViewer } from './pages/ReplayViewer';
import { Reports } from './pages/Reports';
import { Validation } from './pages/Validation';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/replay" element={<ReplayViewer />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/validation" element={<Validation />} />
          </Routes>
        </main>
        <footer className="py-4 border-t border-slate-900 text-center text-xs text-slate-500 font-mono">
          BHID v1.0 Platform &copy; 2026 | Bottleneck Hazard & Intelligence Detection | Localhost Operational Mode
        </footer>
      </div>
    </Router>
  );
};

export default App;
