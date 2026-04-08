'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

type User = { id: number; email: string; full_name: string; role: string };
type Provider = { provider: string; status: string; message: string };
type Report = {
  id: number;
  report_type: string;
  status: string;
  days: number;
  markdown_path?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  result_json?: string | null;
};
type Task = { id: number; title: string; status: string; priority_score: number };
type Content = { id: number; keyword: string; title: string; status: string; current_version: number };
type AuditLog = { id: number; action: string; entity_type: string; entity_id: string; details?: string | null; created_at: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';

async function apiCall<T>(path: string, method = 'GET', token?: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export default function HomePage() {
  const [token, setToken] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState('');

  const [email, setEmail] = useState('admin@zerovape.com');
  const [password, setPassword] = useState('Admin@12345');

  const [settings, setSettings] = useState({
    ga4_property_id: '',
    gsc_site_url: '',
    dataforseo_login: '',
    dataforseo_password: '',
    ai_provider: '',
    ai_api_key: '',
  });

  const [providers, setProviders] = useState<Provider[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [contentItems, setContentItems] = useState<Content[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

  const [keyword, setKeyword] = useState('Best vape products');
  const [contentTitle, setContentTitle] = useState('Top Vape Guide for Beginners');

  const isAdmin = useMemo(() => user?.role === 'admin', [user?.role]);

  const login = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    try {
      const data = await apiCall<{ access_token: string; user: User }>('/auth/login', 'POST', undefined, {
        email,
        password,
      });
      setToken(data.access_token);
      setUser(data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  const loadSettings = async (authToken: string) => {
    try {
      const data = await apiCall<{
        ga4_property_id: string;
        gsc_site_url: string;
        dataforseo_login_masked: string;
        dataforseo_password_masked: string;
        ai_provider: string;
        ai_api_key_masked: string;
      }>('/settings', 'GET', authToken);
      setSettings({
        ga4_property_id: data.ga4_property_id || '',
        gsc_site_url: data.gsc_site_url || '',
        dataforseo_login: data.dataforseo_login_masked || '',
        dataforseo_password: data.dataforseo_password_masked || '',
        ai_provider: data.ai_provider || '',
        ai_api_key: data.ai_api_key_masked || '',
      });
    } catch {
      // Keep form defaults if settings are unavailable.
    }
  };

  useEffect(() => {
    if (!token) return;
    void loadSettings(token);
  }, [token]);

  const saveSettings = async () => {
    setError('');
    try {
      const payload: Record<string, string> = {};

      if (settings.ga4_property_id.trim()) payload.ga4_property_id = settings.ga4_property_id.trim();
      if (settings.gsc_site_url.trim()) payload.gsc_site_url = settings.gsc_site_url.trim();
      if (settings.ai_provider.trim()) payload.ai_provider = settings.ai_provider.trim();

      if (settings.dataforseo_login.trim() && !settings.dataforseo_login.includes('*')) {
        payload.dataforseo_login = settings.dataforseo_login.trim();
      }
      if (settings.dataforseo_password.trim() && !settings.dataforseo_password.includes('*')) {
        payload.dataforseo_password = settings.dataforseo_password.trim();
      }
      if (settings.ai_api_key.trim() && !settings.ai_api_key.includes('*')) {
        payload.ai_api_key = settings.ai_api_key.trim();
      }

      await apiCall('/settings', 'PUT', token, payload);
      await loadSettings(token);
      alert('Settings saved successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save settings failed');
    }
  };

  const testConnections = async () => {
    setError('');
    try {
      const data = await apiCall<{ providers: Provider[] }>('/connections/test', 'POST', token);
      setProviders(data.providers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection test failed');
    }
  };

  const runReport = async () => {
    setError('');
    try {
      await apiCall('/reports/performance-review', 'POST', token, { days: 30 });
      await loadReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Report job failed');
    }
  };

  const loadReports = async () => {
    setError('');
    try {
      const data = await apiCall<Report[]>('/reports', 'GET', token);
      setReports(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Load reports failed');
    }
  };

  const loadReportDetails = async (id: number) => {
    setError('');
    try {
      const data = await apiCall<Report>(`/reports/${id}`, 'GET', token);
      setSelectedReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Load report details failed');
    }
  };

  const createTasksFromReport = async () => {
    if (!selectedReport) return;
    setError('');
    try {
      await apiCall(`/tasks/from-report/${selectedReport.id}`, 'POST', token);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create tasks failed');
    }
  };

  const loadTasks = async () => {
    setError('');
    try {
      const data = await apiCall<Task[]>('/tasks', 'GET', token);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Load tasks failed');
    }
  };

  const moveTask = async (taskId: number, status: string) => {
    setError('');
    try {
      await apiCall(`/tasks/${taskId}/status`, 'PATCH', token, { status });
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update task failed');
    }
  };

  const createBrief = async () => {
    setError('');
    try {
      await apiCall('/content/brief', 'POST', token, { keyword, title: contentTitle });
      await loadContent();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create brief failed');
    }
  };

  const draftContent = async (contentId: number) => {
    await apiCall(`/content/${contentId}/draft`, 'POST', token, { notes: 'Draft generated from brief' });
    await loadContent();
  };

  const optimizeContent = async (contentId: number) => {
    await apiCall(`/content/${contentId}/optimize`, 'POST', token, { notes: 'SEO optimization pass' });
    await loadContent();
  };

  const publishContent = async (contentId: number) => {
    await apiCall(`/publishing/publish/content/${contentId}`, 'POST', token);
    await loadContent();
    await loadAuditLogs();
  };

  const loadContent = async () => {
    const data = await apiCall<Content[]>('/content', 'GET', token);
    setContentItems(data);
  };

  const exportSelectedReport = async (format: 'markdown' | 'csv') => {
    if (!selectedReport) return;
    await apiCall(`/publishing/export/report/${selectedReport.id}?format=${format}`, 'POST', token);
    await loadAuditLogs();
    alert('Export completed');
  };

  const loadAuditLogs = async () => {
    const data = await apiCall<AuditLog[]>('/publishing/audit-logs', 'GET', token);
    setAuditLogs(data);
  };

  return (
    <main className="container">
      <h1>Zero Vape SEO Platform</h1>
      <p className="small">Phases 0-7 (MVP+): Auth, Settings, Connections, Reports, Tasks, Content, Publishing, Audit</p>

      {error ? <p className="status-failed">{error}</p> : null}

      {!token ? (
        <section className="card" style={{ maxWidth: 420 }}>
          <h2>Login</h2>
          <form onSubmit={login}>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
            <button type="submit">Sign In</button>
          </form>
          <p className="small">Default admin: admin@zerovape.com / Admin@12345</p>
        </section>
      ) : (
        <>
          <div className="card">
            <h3>User Information</h3>
            <p>
              {user?.full_name} - {user?.email} - <b>{user?.role}</b>
            </p>
          </div>

          <div className="grid">
            <section className="card">
              <h2>Settings</h2>
              <input placeholder="GA4 Property ID" value={settings.ga4_property_id} onChange={(e) => setSettings((s) => ({ ...s, ga4_property_id: e.target.value }))} disabled={!isAdmin} />
              <input placeholder="GSC Site URL" value={settings.gsc_site_url} onChange={(e) => setSettings((s) => ({ ...s, gsc_site_url: e.target.value }))} disabled={!isAdmin} />
              <input placeholder="DataForSEO Login" value={settings.dataforseo_login} onChange={(e) => setSettings((s) => ({ ...s, dataforseo_login: e.target.value }))} disabled={!isAdmin} />
              <input placeholder="DataForSEO Password" type="password" value={settings.dataforseo_password} onChange={(e) => setSettings((s) => ({ ...s, dataforseo_password: e.target.value }))} disabled={!isAdmin} />
              <input placeholder="AI Provider" value={settings.ai_provider} onChange={(e) => setSettings((s) => ({ ...s, ai_provider: e.target.value }))} disabled={!isAdmin} />
              <input placeholder="AI API Key" value={settings.ai_api_key} onChange={(e) => setSettings((s) => ({ ...s, ai_api_key: e.target.value }))} disabled={!isAdmin} />
              <button onClick={saveSettings} disabled={!isAdmin}>Save Settings</button>
            </section>

            <section className="card">
              <h2>Connection Tests</h2>
              <button onClick={testConnections}>Test Connections</button>
              {providers.map((item) => (
                <div key={item.provider}>
                  <b>{item.provider}:</b>{' '}
                  <span className={item.status === 'connected' ? 'status-ok' : 'status-failed'}>{item.status}</span>
                  <div className="small">{item.message}</div>
                </div>
              ))}
            </section>

            <section className="card">
              <h2>Performance Reports</h2>
              <button onClick={runReport}>Run Performance Review</button>
              <button className="secondary" onClick={loadReports}>Load Reports</button>
              {reports.map((report) => (
                <div key={report.id} style={{ marginBottom: 10, borderTop: '1px solid #e5e7eb', paddingTop: 8 }}>
                  <div>#{report.id} - {report.status}</div>
                  <button onClick={() => loadReportDetails(report.id)}>View Details</button>
                </div>
              ))}
            </section>

            <section className="card">
              <h2>Task Board</h2>
              <button onClick={loadTasks}>Load Tasks</button>
              <button onClick={createTasksFromReport} disabled={!selectedReport}>Create Tasks from Selected Report</button>
              {tasks.map((task) => (
                <div key={task.id} style={{ marginBottom: 8, borderTop: '1px solid #e5e7eb', paddingTop: 8 }}>
                  <div><b>{task.title}</b> - {task.status} - Score {task.priority_score}</div>
                  <button onClick={() => moveTask(task.id, 'todo')}>To Do</button>
                  <button onClick={() => moveTask(task.id, 'in_progress')}>In Progress</button>
                  <button onClick={() => moveTask(task.id, 'done')}>Done</button>
                </div>
              ))}
            </section>

            <section className="card">
              <h2>Content Pipeline</h2>
              <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Keyword" />
              <input value={contentTitle} onChange={(e) => setContentTitle(e.target.value)} placeholder="Content Title" />
              <button onClick={createBrief}>Create Brief</button>
              <button className="secondary" onClick={loadContent}>Load Content</button>
              {contentItems.map((item) => (
                <div key={item.id} style={{ marginBottom: 8, borderTop: '1px solid #e5e7eb', paddingTop: 8 }}>
                  <div><b>{item.title}</b> - {item.status} - v{item.current_version}</div>
                  <button onClick={() => draftContent(item.id)}>Draft</button>
                  <button onClick={() => optimizeContent(item.id)}>Optimize</button>
                  <button onClick={() => publishContent(item.id)}>Publish</button>
                </div>
              ))}
            </section>

            <section className="card">
              <h2>Publishing + Audit</h2>
              <button onClick={() => exportSelectedReport('markdown')} disabled={!selectedReport}>Export Markdown</button>
              <button onClick={() => exportSelectedReport('csv')} disabled={!selectedReport}>Export CSV</button>
              <button className="secondary" onClick={loadAuditLogs}>Load Audit Logs</button>
              {auditLogs.map((log) => (
                <div key={log.id} style={{ marginBottom: 8, borderTop: '1px solid #e5e7eb', paddingTop: 8 }}>
                  <div><b>{log.action}</b> - {log.entity_type}:{log.entity_id}</div>
                  <div className="small">{log.details}</div>
                </div>
              ))}
            </section>
          </div>

          {selectedReport ? (
            <section className="card">
              <h2>Report Details #{selectedReport.id}</h2>
              <p>Status: <b>{selectedReport.status}</b></p>
              <p>markdown: {selectedReport.markdown_path || 'N/A'}</p>
              <pre>{selectedReport.result_json || 'No report body yet'}</pre>
            </section>
          ) : null}
        </>
      )}
    </main>
  );
}
