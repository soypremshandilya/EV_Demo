import { useState, useEffect } from 'react'
import { Bike, Battery, Users, IndianRupee, Zap, Activity, TrendingUp } from 'lucide-react'
import API from '../../config'

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch(`${API}/dashboard/stats`)
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(() => {})
  }, [])

  const cards = [
    {
      icon: Bike,
      label: 'Total Scooters',
      value: stats?.total_scooters ?? '—',
      color: 'var(--accent)',
    },
    {
      icon: Zap,
      label: 'Available',
      value: stats?.available_scooters ?? '—',
      color: 'var(--success)',
    },
    {
      icon: Battery,
      label: 'Charging',
      value: stats?.charging_scooters ?? '—',
      color: 'var(--warning)',
    },
    {
      icon: Users,
      label: 'Customers',
      value: stats?.total_customers ?? '—',
      color: 'var(--info)',
    },
    {
      icon: IndianRupee,
      label: 'Total Revenue',
      value: stats ? `₹${stats.total_revenue.toLocaleString('en-IN')}` : '—',
      color: '#a78bfa',
    },
    {
      icon: Activity,
      label: 'Avg Battery',
      value: stats ? `${stats.avg_battery}%` : '—',
      color: stats && stats.avg_battery >= 50 ? 'var(--success)' : 'var(--warning)',
    },
  ]

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Real-time overview of your EV scooter fleet operations</p>
      </div>

      {/* Stats Grid */}
      <div className="card-grid" style={{ marginBottom: 'var(--space-8)' }}>
        {cards.map((card, i) => (
          <div
            key={card.label}
            className={`card stat-card animate-fade-in animate-fade-in-delay-${Math.min(i + 1, 4)}`}
          >
            <div className="stat-icon" style={{ background: `${card.color}18`, color: card.color }}>
              <card.icon size={22} />
            </div>
            <div className="stat-value">{card.value}</div>
            <div className="stat-label">{card.label}</div>
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
              Chart visualisation coming soon
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
