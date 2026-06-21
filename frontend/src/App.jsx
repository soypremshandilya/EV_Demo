import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import Dashboard from './pages/Dashboard/Dashboard'
import Scooters from './pages/Scooters/Scooters'
import Batteries from './pages/Batteries/Batteries'
import Customers from './pages/Customers/Customers'
import Rentals from './pages/Rentals/Rentals'
import AIChat from './pages/AIChat/AIChat'

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scooters" element={<Scooters />} />
          <Route path="/batteries" element={<Batteries />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/rentals" element={<Rentals />} />
          <Route path="/chat" element={<AIChat />} />
        </Routes>
      </main>
    </div>
  )
}
