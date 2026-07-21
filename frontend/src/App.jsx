<<<<<<< HEAD
import React, { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://127.0.0.1:8000';
=======
import React, { useState, useEffect } from 'react';
>>>>>>> 03bb09388a7358a79f7e23d2506e3e1b2433c892

export default function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

<<<<<<< HEAD
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
=======
  useEffect(() => {
    // Use environment variable for API URL, fallback to localhost for development
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    const endpoint = `${apiUrl}/api/analytics/watchlist`;
    
    fetch(endpoint)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(json => {
        // Updated to match the new API response structure
        setWatchlist(json.watchlist || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.toString());
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: '30px', background: '#0f172a', color: '#fff', minHeight: '100vh', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ borderBottom: '1px solid #334155', marginBottom: '30px', paddingBottom: '10px' }}>
        <h1 style={{ color: '#38bdf8', margin: 0 }}>⚽ Blue Lock Analytics Platform</h1>
        <p style={{ color: '#94a3b8', marginTop: '5px' }}>Professional Telemetry & Anomaly Dashboard</p>
      </header>

      {loading && <p>Loading data from backend...</p>}
      {error && (
        <div style={{ background: '#450a0a', border: '1px solid #991b1b', padding: '15px', borderRadius: '8px', color: '#fca5a5' }}>
          <strong>Connection Error:</strong> {error}
          <p style={{ fontSize: '0.8em', marginTop: '10px' }}>Ensure the FastAPI backend is running on port 8000 or check environment configuration.</p>
        </div>
      )}

      {!loading && !error && (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', background: '#1e293b', borderRadius: '8px', overflow: 'hidden' }}>
            <thead>
              <tr style={{ background: '#334155', textAlign: 'left' }}>
                <th style={{ padding: '15px' }}>Device ID</th>
                <th style={{ padding: '15px' }}>Drift Index</th>
                <th style={{ padding: '15px' }}>Status</th>
                <th style={{ padding: '15px' }}>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {watchlist.length > 0 ? watchlist.map((item, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #475569', transition: 'background 0.2s' }} 
                    onMouseOver={(e) => e.currentTarget.style.background = '#334155'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '15px', fontWeight: 'bold' }}>{item.device_id}</td>
                  <td style={{ padding: '15px' }}>{item.drift_index}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ 
                      background: item.status === 'CRITICAL_ANOMALY' ? '#7f1d1d' : '#064e3b', 
                      color: item.status === 'CRITICAL_ANOMALY' ? '#fca5a5' : '#6ee7b7', 
                      padding: '4px 10px', 
                      borderRadius: '12px',
                      fontSize: '0.85em',
                      fontWeight: 'bold'
                    }}>
                      {item.status}
                    </span>
                  </td>
                  <td style={{ padding: '15px', color: '#94a3b8', fontSize: '0.9em' }}>{item.timestamp}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>
                    No critical anomalies detected. System healthy.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
>>>>>>> 03bb09388a7358a79f7e23d2506e3e1b2433c892
      )}
    </div>
  );
}
