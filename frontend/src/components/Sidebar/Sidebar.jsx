import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Bike,
  Battery,
  Users,
  Receipt,
  MessageSquare,
  Zap
} from 'lucide-react'
import './Sidebar.css'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/scooters', icon: Bike, label: 'Scooters' },
  { to: '/batteries', icon: Battery, label: 'Batteries' },
  { to: '/customers', icon: Users, label: 'Customers' },
  { to: '/rentals', icon: Receipt, label: 'Rentals' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar" id="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <Zap size={22} />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-name">VoltRide AI</span>
          <span className="sidebar-brand-label">Operations Hub</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Operations</div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `sidebar-link${isActive ? ' active' : ''}`
            }
            id={`nav-${label.toLowerCase()}`}
          >
            <Icon className="sidebar-link-icon" />
            <span>{label}</span>
          </NavLink>
        ))}

        <div className="sidebar-section-label" style={{ marginTop: '0.5rem' }}>
          Intelligence
        </div>
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            `sidebar-link${isActive ? ' active' : ''}`
          }
          id="nav-aichat"
        >
          <MessageSquare className="sidebar-link-icon" />
          <span>AI Chat</span>
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-badge">
          <span className="sidebar-footer-dot"></span>
          <span>Gemini 2.5 Flash · Read Only</span>
        </div>
      </div>
    </aside>
  )
}
