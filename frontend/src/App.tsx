import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { LeadsPage } from './pages/LeadsPage';
import { AutomationPage } from './pages/AutomationPage';
import { EmailHistoryPage } from './pages/EmailHistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { fetchHealth } from './services/api';
import type { HealthStatus } from './types';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  const loadHealthStatus = async () => {
    setLoadingHealth(true);
    const data = await fetchHealth();
    setHealth(data);
    setLoadingHealth(false);
  };

  useEffect(() => {
    loadHealthStatus();
  }, []);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans antialiased">
        {/* Dark Navy Sidebar */}
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Main Content Workspace */}
        <div className="flex-1 flex flex-col min-w-0">
          <Header
            onMenuToggle={() => setSidebarOpen(prev => !prev)}
            health={health}
            onRefreshHealth={loadHealthStatus}
            isDemoData={true}
          />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Routes>
              {/* 1. Dashboard Overview */}
              <Route
                path="/"
                element={
                  <OverviewPage
                    health={health}
                    loadingHealth={loadingHealth}
                    onRefreshHealth={loadHealthStatus}
                  />
                }
              />

              {/* 2. All Leads */}
              <Route
                path="/leads"
                element={
                  <LeadsPage
                    key="all-leads"
                    pageTitle="All Inbound Leads"
                    initialPriorityFilter="All"
                  />
                }
              />

              {/* 3. High Priority Leads */}
              <Route
                path="/leads/high-priority"
                element={
                  <LeadsPage
                    key="high-priority-leads"
                    pageTitle="High Priority Leads"
                    initialPriorityFilter="High"
                  />
                }
              />

              {/* 4. Automation Workflow & Integrations */}
              <Route path="/automation" element={<AutomationPage />} />

              {/* 5. Email History */}
              <Route path="/emails" element={<EmailHistoryPage />} />

              {/* 6. Settings */}
              <Route
                path="/settings"
                element={
                  <SettingsPage
                    health={health}
                    loadingHealth={loadingHealth}
                    onRefreshHealth={loadHealthStatus}
                  />
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
