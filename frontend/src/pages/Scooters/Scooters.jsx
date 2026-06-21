import { Bike } from 'lucide-react'

export default function Scooters() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Scooters</h1>
        <p className="page-subtitle">Fleet inventory and scooter status tracking</p>
      </div>

      <div className="table-placeholder animate-fade-in animate-fade-in-delay-1">
        <div className="table-placeholder-icon">
          <Bike size={28} />
        </div>
        <h3>No Scooter Data Yet</h3>
        <p>Scooter inventory will appear here once the database is connected and populated.</p>
      </div>
    </div>
  )
}
