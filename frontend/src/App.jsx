import React, { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWatchlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/analytics/watchlist`);
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const json = await res.json();
      setWatchlist(json.data || []);
    } catch (err) {
      setError(err.message || 'Could not reach the analytics API.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', background: '#0f172a', color: '#f8fafc', minHeight: '100vh' }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#38bdf8', margin: 0 }}>Blue Lock Analytics</h1>
        <p style={{ color: '#94a3b8' }}>Live telemetry &amp; anomaly watchlist</p>
      </header>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>Critical Risk Watchlist</h2>
        <button
          onClick={fetchWatchlist}
          style={{ padding: '0.5rem 1rem', background: '#0284c7', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
        >
          Refresh
        </button>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: '#f87171' }}>Error: {error}</p>}

      {!loading && !error && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#1e293b', textAlign: 'left' }}>
              <th style={{ padding: '0.75rem' }}>Device</th>
              <th style={{ padding: '0.75rem' }}>Date</th>
              <th style={{ padding: '0.75rem' }}>Anomaly Minutes</th>
              <th style={{ padding: '0.75rem' }}>Risk</th>
            </tr>
          </thead>
          <tbody>
            {watchlist.length === 0 && (
              <tr><td colSpan={4} style={{ padding: '0.75rem', color: '#94a3b8' }}>No critical devices right now.</td></tr>
            )}
            {watchlist.map((item, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #334155' }}>
                <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>{item.device_id}</td>
                <td style={{ padding: '0.75rem' }}>{item.tracking_date}</td>
                <td style={{ padding: '0.75rem' }}>{Number(item.total_anomaly_minutes).toFixed(2)}</td>
                <td style={{ padding: '0.75rem' }}>
                  <span style={{ background: '#7f1d1d', color: '#fca5a5', padding: '0.25rem 0.5rem', borderRadius: 4 }}>
                    {item.exposure_risk_rating}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
