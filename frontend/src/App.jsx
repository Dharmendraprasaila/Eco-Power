import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Installations from './pages/Installations'
import Analytics from './pages/Analytics'
import Reports from './pages/Reports'
import { Sun, BarChart3, Settings, FileText, AlertTriangle } from 'lucide-react'

function App() {
  const [notifications, setNotifications] = useState([])

  // Fetch notifications on app load
  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchNotifications = async () => {
    try {
      // This would fetch from all installations - simplified for demo
      const response = await fetch('/api/alerts/INST_001')
      if (response.ok) {
        const alerts = await response.json()
        setNotifications(alerts.slice(0, 3)) // Show top 3 alerts
      }
    } catch (error) {
      console.error('Error fetching notifications:', error)
    }
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation Header */}
        <nav className="bg-white shadow-lg border-b">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-2">
                  <Sun className="h-8 w-8 text-yellow-500" />
                  <span className="text-xl font-bold text-gray-900">SolarMax Pro</span>
                </div>
                
                <div className="hidden md:flex space-x-6">
                  <Link to="/" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md">
                    <BarChart3 className="h-4 w-4" />
                    <span>Dashboard</span>
                  </Link>
                  <Link to="/installations" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md">
                    <Settings className="h-4 w-4" />
                    <span>Installations</span>
                  </Link>
                  <Link to="/analytics" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md">
                    <BarChart3 className="h-4 w-4" />
                    <span>Analytics</span>
                  </Link>
                  <Link to="/reports" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md">
                    <FileText className="h-4 w-4" />
                    <span>Reports</span>
                  </Link>
                </div>
              </div>

              {/* Notifications */}
              <div className="flex items-center space-x-4">
                {notifications.length > 0 && (
                  <div className="relative">
                    <AlertTriangle className="h-6 w-6 text-red-500" />
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {notifications.length}
                    </span>
                  </div>
                )}
                <div className="text-sm text-gray-600">
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Alert Banner */}
        {notifications.length > 0 && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="max-w-7xl mx-auto">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-700">
                    <strong>Active Alerts:</strong> {notifications[0].message}
                    {notifications.length > 1 && ` (+${notifications.length - 1} more)`}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 px-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/installations" element={<Installations />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App