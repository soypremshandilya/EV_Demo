import { useState, useEffect } from 'react'
import { Receipt } from 'lucide-react'

const API = 'http://localhost:8000'

export default function Rentals() {
  const [rentals, setRentals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/rentals`)
      .then(res => res.json())
      .then(data => { setRentals(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Rentals</h1>
        <p className="page-subtitle">Active and historical rental transactions</p>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading rentals…</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          <Receipt size={28} />
          <p>Failed to load rentals: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="data-table-wrapper animate-fade-in animate-fade-in-delay-1">
          <table className="data-table" id="rentals-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Scooter ID</th>
                <th>Customer ID</th>
                <th>Duration</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {rentals.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.scooter_id}</td>
                  <td>{r.customer_id}</td>
                  <td>{r.duration_hours}h</td>
                  <td>₹{r.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
