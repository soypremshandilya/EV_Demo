import { Receipt } from 'lucide-react'

export default function Rentals() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Rentals</h1>
        <p className="page-subtitle">Active and historical rental transactions</p>
      </div>

      <div className="table-placeholder animate-fade-in animate-fade-in-delay-1">
        <div className="table-placeholder-icon">
          <Receipt size={28} />
        </div>
        <h3>No Rental Data Yet</h3>
        <p>Hourly, daily, and monthly rental records will appear here once the database is connected.</p>
      </div>
    </div>
  )
}
