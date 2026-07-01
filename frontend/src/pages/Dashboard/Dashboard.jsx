import { useState, useEffect } from 'react'
import { Bike, Battery, Users, Receipt, TrendingUp, Activity } from 'lucide-react'

const API = 'http://localhost:8000'

export default function Dashboard() {
  const [counts, setCounts] = useState({ scooters: '—', batteries: '—', customers: '—', rentals: '—' })

  useEffect(() => {
    Promise.all([
      fetch(`${API}/scooters`).then(r => r.json()),
      fetch(`${API}/batteries`).then(r => r.json()),
      fetch(`${API}/customers`).then(r => r.json()),
      fetch(`${API}/rentals`).then(r => r.json()),
    ])
      .then(([s, b, c, r]) => {
        setCounts({
          scooters: s.length,
          batteries: b.length,
          customers: c.length,
          rentals: r.length,
        })
      })
      .catch(() => {})
  }, [])

  const stats = [
    { icon: Bike, label: 'Total Scooters', value: counts.scooters, color: 'var(--accent)' },
    { icon: Battery, label: 'Active Batteries', value: counts.batteries, color: 'var(--info)' },
    { icon: Users, label: 'Customers', value: counts.customers, color: 'var(--success)' },
    { icon: Receipt, label: 'Active Rentals', value: counts.rentals, color: 'var(--warning)' },
  ]

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Real-time overview of your EV scooter fleet operations</p>
      </div>

      {/* Stats Grid */}
      <div className="card-grid" style={{ marginBottom: 'var(--space-8)' }}>
        {stats.map((stat, i) => (
          <div
            key={stat.label}
            className={`card stat-card animate-fade-in animate-fade-in-delay-${i + 1}`}
          >
            <div className="stat-icon" style={{ background: `${stat.color}18`, color: stat.color }}>
              <stat.icon size={22} />
            </div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Placeholder Panels */}
      <div className="card-grid">
        <div className="card animate-fade-in animate-fade-in-delay-3" style={{ gridColumn: 'span 2' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
            <TrendingUp size={20} style={{ color: 'var(--accent)' }} />
            <h3 style={{ fontSize: 'var(--font-md)', fontWeight: 600 }}>Revenue Trend</h3>
          </div>
          <div className="table-placeholder" style={{ border: 'none', padding: 'var(--space-8)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-sm)' }}>
              Chart will render once the database is connected
            </p>
          </div>
        </div>
        <div className="card animate-fade-in animate-fade-in-delay-4">
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
            <Activity size={20} style={{ color: 'var(--success)' }} />
            <h3 style={{ fontSize: 'var(--font-md)', fontWeight: 600 }}>Fleet Health</h3>
          </div>
          <div className="table-placeholder" style={{ border: 'none', padding: 'var(--space-8)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-sm)' }}>
              Status breakdown coming soon
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
