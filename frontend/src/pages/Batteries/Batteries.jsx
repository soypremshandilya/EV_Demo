import { useState, useEffect } from 'react'
import { Battery } from 'lucide-react'
import API from '../../config'

function getLevelColor(level) {
  if (level >= 60) return 'var(--success)'
  if (level >= 30) return 'var(--warning)'
  return 'var(--danger)'
}

export default function Batteries() {
  const [batteries, setBatteries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/batteries`)
      .then(res => res.json())
      .then(data => { setBatteries(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Batteries</h1>
        <p className="page-subtitle">Swappable battery pool management and health monitoring</p>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading batteries…</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          <Battery size={28} />
          <p>Failed to load batteries: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="data-table-wrapper animate-fade-in animate-fade-in-delay-1">
          <table className="data-table" id="batteries-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Station Name</th>
                <th>Battery Level</th>
              </tr>
            </thead>
            <tbody>
              {batteries.map(b => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{b.station_name}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="battery-bar">
                        <div
                          className="battery-bar-fill"
                          style={{
                            width: `${b.battery_level}%`,
                            background: getLevelColor(b.battery_level),
                          }}
                        />
                      </div>
                      <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                        {b.battery_level}%
                      </span>
                    </div>
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
