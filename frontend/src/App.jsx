import React, { useState, useEffect } from 'react';

export default function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Updated to point to consolidated FastAPI server on port 8000
    fetch('http://127.0.0.1:8000/api/analytics/watchlist')
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
          <p style={{ fontSize: '0.8em', marginTop: '10px' }}>Ensure the FastAPI backend is running on port 8000.</p>
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
      )}
    </div>
  );
}
