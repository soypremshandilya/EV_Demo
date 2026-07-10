import { useState, useEffect } from 'react'
import { Bike } from 'lucide-react'
import API from '../../config'

function getBatteryColor(pct) {
  if (pct >= 60) return 'var(--success)'
  if (pct >= 30) return 'var(--warning)'
  return 'var(--danger)'
}

export default function Scooters() {
  const [scooters, setScooters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/scooters`)
      .then(res => res.json())
      .then(data => { setScooters(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Scooters</h1>
        <p className="page-subtitle">Fleet inventory and scooter status tracking</p>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading scooters…</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          <Bike size={28} />
          <p>Failed to load scooters: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="data-table-wrapper animate-fade-in animate-fade-in-delay-1">
          <table className="data-table" id="scooters-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Location</th>
                <th>Battery</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {scooters.map(s => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.name}</td>
                  <td>{s.location}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="battery-bar">
                        <div
                          className="battery-bar-fill"
                          style={{
                            width: `${s.battery_percentage}%`,
                            background: getBatteryColor(s.battery_percentage),
                          }}
                        />
                      </div>
                      <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                        {s.battery_percentage}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${s.status}`}>{s.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
