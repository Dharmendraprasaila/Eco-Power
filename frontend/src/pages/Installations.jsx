import React, { useState, useEffect } from 'react'
import { MapPin, Zap, Calendar, Thermometer } from 'lucide-react'

const Installations = () => {
  const [installations, setInstallations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInstallations()
  }, [])

  const fetchInstallations = async () => {
    try {
      const response = await fetch('/api/installations')
      if (response.ok) {
        const data = await response.json()
        setInstallations(data)
      }
    } catch (error) {
      console.error('Error fetching installations:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center py-8">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Solar Installations</h1>
        <p className="text-gray-600">Manage and monitor your solar installations across India</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {installations.map(installation => (
          <div key={installation.id} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{installation.name}</h3>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Active
              </span>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center text-gray-600">
                <MapPin className="h-4 w-4 mr-2" />
                <span className="text-sm">{installation.location}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <Zap className="h-4 w-4 mr-2" />
                <span className="text-sm">{installation.capacity_kw} kW Capacity</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <Thermometer className="h-4 w-4 mr-2" />
                <span className="text-sm">{installation.climatic_zone} Zone</span>
              </div>
              
              <div className="text-gray-600">
                <span className="text-sm">{installation.panel_count} Solar Panels</span>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Installations