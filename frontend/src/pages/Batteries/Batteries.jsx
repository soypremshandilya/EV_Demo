import { Battery } from 'lucide-react'

export default function Batteries() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Batteries</h1>
        <p className="page-subtitle">Swappable battery pool management and health monitoring</p>
      </div>

      <div className="table-placeholder animate-fade-in animate-fade-in-delay-1">
        <div className="table-placeholder-icon">
          <Battery size={28} />
        </div>
        <h3>No Battery Data Yet</h3>
        <p>Battery inventory and charge levels will appear here once the database is connected.</p>
      </div>
    </div>
  )
}
