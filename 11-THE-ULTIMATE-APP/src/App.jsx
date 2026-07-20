import React, { useState, useEffect } from 'react';

export default function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5001/api/analytics/watchlist')
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success' || json.data) {
          setWatchlist(json.data || []);
        } else {
          setError('Failed to load data structure');
        }
        setLoading(false);
      })
      .catch(err => {
        setError(err.toString());
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: '30px', background: '#0f172a', color: '#fff', minHeight: '100vh', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#38bdf8' }}>⚽ Blue Lock Analytics Platform</h1>
      <p style={{ color: '#94a3b8' }}>Live Telemetry & Anomaly Dashboard</p>

      {loading && <p>Loading data from backend...</p>}
      {error && <p style={{ color: '#ef4444' }}>Error: {error}</p>}

      {!loading && !error && (
        <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', background: '#1e293b' }}>
          <thead>
            <tr style={{ background: '#334155', textAlign: 'left' }}>
              <th style={{ padding: '12px' }}>Device ID</th>
              <th style={{ padding: '12px' }}>Tracking Date</th>
              <th style={{ padding: '12px' }}>Anomaly Minutes</th>
              <th style={{ padding: '12px' }}>Risk Rating</th>
            </tr>
          </thead>
          <tbody>
            {watchlist.map((item, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #475569' }}>
                <td style={{ padding: '12px', fontWeight: 'bold' }}>{item.device_id}</td>
                <td style={{ padding: '12px' }}>{item.tracking_date}</td>
                <td style={{ padding: '12px' }}>{Number(item.total_anomaly_minutes).toFixed(2)} mins</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ background: '#7f1d1d', color: '#fca5a5', padding: '4px 8px', borderRadius: '4px' }}>
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