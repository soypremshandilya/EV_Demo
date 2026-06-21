import { Users } from 'lucide-react'

export default function Customers() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Customers</h1>
        <p className="page-subtitle">Customer directory and subscription history</p>
      </div>

      <div className="table-placeholder animate-fade-in animate-fade-in-delay-1">
        <div className="table-placeholder-icon">
          <Users size={28} />
        </div>
        <h3>No Customer Data Yet</h3>
        <p>Customer records and rental history will appear here once the database is connected.</p>
      </div>
    </div>
  )
}
