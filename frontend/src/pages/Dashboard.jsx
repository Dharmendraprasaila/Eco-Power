import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { Sun, Zap, Thermometer, Wind, Droplets, AlertTriangle, TrendingUp, Battery } from 'lucide-react'

const Dashboard = () => {
  const [installations, setInstallations] = useState([])
  const [selectedInstallation, setSelectedInstallation] = useState('INST_001')
  const [telemetryData, setTelemetryData] = useState([])
  const [predictions, setPredictions] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [realTimeData, setRealTimeData] = useState(null)

  useEffect(() => {
    fetchInstallations()
    fetchDashboardData()
    
    // Set up real-time updates
    const interval = setInterval(fetchDashboardData, 15000) // Update every 15 seconds
    return () => clearInterval(interval)
  }, [selectedInstallation])

  const fetchInstallations = async () => {
    try {
      const response = await fetch('/api/installations')
      if (response.ok) {
        const data = await response.json()
        setInstallations(data)
      }
    } catch (error) {
      console.error('Error fetching installations:', error)
    }
  }

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      const [telemetryRes, predictionsRes, alertsRes] = await Promise.all([
        fetch(`/api/latest/${selectedInstallation}`),
        fetch(`/api/predictions/${selectedInstallation}`),
        fetch(`/api/alerts/${selectedInstallation}`)
      ])

      if (telemetryRes.ok) {
        const telemetryData = await telemetryRes.json()
        setTelemetryData(telemetryData)
        setRealTimeData(telemetryData[0]) // Latest data point
      }

      if (predictionsRes.ok) {
        const predictionsData = await predictionsRes.json()
        setPredictions(predictionsData)
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json()
        setAlerts(alertsData)
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/report/${selectedInstallation}`)
      if (response.ok) {
        const data = await response.json()
        // Open report in new window
        const newWindow = window.open('', '_blank')
        newWindow.document.write(`
          <html>
            <head><title>Solar Performance Report</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px; line-height: 1.6;">
              <h1>Solar Performance Report</h1>
              <pre style="white-space: pre-wrap;">${data.report}</pre>
            </body>
          </html>
        `)
      }
    } catch (error) {
      console.error('Error generating report:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate performance metrics
  const calculateMetrics = () => {
    if (!telemetryData.length) return {}
    
    const latest = telemetryData[0]
    const avgPower = telemetryData.reduce((sum, d) => sum + d.pv_power_kw, 0) / telemetryData.length
    const maxPower = Math.max(...telemetryData.map(d => d.pv_power_kw))
    const avgEfficiency = predictions.length ? predictions.reduce((sum, p) => sum + p.efficiency_score, 0) / predictions.length : 0
    
    return {
      currentPower: latest?.pv_power_kw || 0,
      avgPower,
      maxPower,
      efficiency: avgEfficiency * 100,
      temperature: latest?.module_temp_c || 0,
      irradiation: latest?.irradiation_wm2 || 0,
      dustLevel: (latest?.dust_level || 0) * 100
    }
  }

  const metrics = calculateMetrics()

  // Prepare chart data
  const chartData = telemetryData.slice(0, 20).reverse().map(d => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    power: d.pv_power_kw,
    irradiation: d.irradiation_wm2 / 10, // Scale for visibility
    temperature: d.module_temp_c,
    efficiency: d.inverter_efficiency
  }))

  const alertColors = {
    HIGH: 'text-red-600 bg-red-50 border-red-200',
    MEDIUM: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    LOW: 'text-blue-600 bg-blue-50 border-blue-200'
  }

  if (loading && !telemetryData.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Solar Energy Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring and intelligent analytics</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select 
            value={selectedInstallation}
            onChange={(e) => setSelectedInstallation(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            {installations.map(inst => (
              <option key={inst.id} value={inst.id}>
                {inst.name} ({inst.capacity_kw}kW)
              </option>
            ))}
          </select>
          
          <button 
            onClick={generateReport}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'AI Report'}
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Current Power</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.currentPower?.toFixed(2)} kW</p>
            </div>
            <Zap className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Efficiency</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.efficiency?.toFixed(1)}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Temperature</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.temperature?.toFixed(1)}°C</p>
            </div>
            <Thermometer className="h-8 w-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Irradiation</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.irradiation?.toFixed(0)} W/m²</p>
            </div>
            <Sun className="h-8 w-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Power Generation Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Real-time Power Generation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="power" stroke="#2563eb" strokeWidth={2} name="Power (kW)" />
              <Line type="monotone" dataKey="irradiation" stroke="#f59e0b" strokeWidth={2} name="Irradiation (W/m²÷10)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Temperature & Efficiency Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Temperature & Efficiency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="temperature" stroke="#dc2626" strokeWidth={2} name="Temperature (°C)" />
              <Line type="monotone" dataKey="efficiency" stroke="#16a34a" strokeWidth={2} name="Efficiency (%)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts and Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Alerts */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-red-500" />
            Active Alerts ({alerts.length})
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No active alerts</p>
            ) : (
              alerts.map(alert => (
                <div key={alert.id} className={`p-3 rounded-md border ${alertColors[alert.severity]}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{alert.alert_type.replace('_', ' ')}</p>
                      <p className="text-sm mt-1">{alert.message}</p>
                    </div>
                    <span className="text-xs font-medium px-2 py-1 rounded">
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs mt-2 opacity-75">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* ML Predictions */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">ML Predictions & Maintenance</h3>
          {predictions.length > 0 ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Predicted Power</p>
                  <p className="text-xl font-bold text-blue-600">
                    {predictions[0]?.predicted_power_kw?.toFixed(2)} kW
                  </p>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">Efficiency Score</p>
                  <p className="text-xl font-bold text-green-600">
                    {(predictions[0]?.efficiency_score * 100)?.toFixed(1)}%
                  </p>
                </div>
              </div>
              
              <div className="p-3 bg-yellow-50 rounded-lg">
                <p className="text-sm text-gray-600">Maintenance Score</p>
                <div className="flex items-center mt-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-yellow-500 h-2 rounded-full" 
                      style={{width: `${predictions[0]?.maintenance_score || 0}%`}}
                    ></div>
                  </div>
                  <span className="ml-2 text-sm font-medium">
                    {predictions[0]?.maintenance_score?.toFixed(0)}/100
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No prediction data available</p>
          )}
        </div>
      </div>

      {/* Environmental Conditions */}
      {realTimeData && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Current Environmental Conditions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Wind className="h-6 w-6 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">Wind Speed</p>
                <p className="font-semibold">{realTimeData.wind_speed_ms} m/s</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Droplets className="h-6 w-6 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">Humidity</p>
                <p className="font-semibold">{realTimeData.humidity_percent}%</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Sun className="h-6 w-6 text-yellow-500" />
              <div>
                <p className="text-sm text-gray-600">Dust Level</p>
                <p className="font-semibold">{(realTimeData.dust_level * 100).toFixed(1)}%</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Battery className="h-6 w-6 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">Inverter Eff.</p>
                <p className="font-semibold">{realTimeData.inverter_efficiency}%</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard