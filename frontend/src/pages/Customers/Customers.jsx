import { useState, useEffect } from 'react'
import { Users } from 'lucide-react'
import API from '../../config'

export default function Customers() {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/customers`)
      .then(res => res.json())
      .then(data => { setCustomers(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Customers</h1>
        <p className="page-subtitle">Customer directory and subscription history</p>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading customers…</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          <Users size={28} />
          <p>Failed to load customers: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="data-table-wrapper animate-fade-in animate-fade-in-delay-1">
          <table className="data-table" id="customers-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Total Rides</th>
                <th>Total Payment</th>
              </tr>
            </thead>
            <tbody>
              {customers.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.total_rides}</td>
                  <td>₹{c.total_payment.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
