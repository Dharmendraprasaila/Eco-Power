import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState([])
  const [selectedMetric, setSelectedMetric] = useState('power')

  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    // This would fetch aggregated analytics data
    // For demo, we'll create sample data
    const sampleData = [
      { name: 'Mumbai', power: 4.2, efficiency: 85, maintenance: 25 },
      { name: 'Delhi', power: 42.5, efficiency: 78, maintenance: 45 },
      { name: 'Bangalore', power: 89.3, efficiency: 92, maintenance: 15 },
      { name: 'Chennai', power: 21.8, efficiency: 88, maintenance: 30 },
      { name: 'Jaipur', power: 178.5, efficiency: 82, maintenance: 55 }
    ]
    setAnalyticsData(sampleData)
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Performance Analytics</h1>
        <p className="text-gray-600">Deep insights into your solar installations</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Installation Comparison</h3>
          <select 
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="power">Power Generation</option>
            <option value="efficiency">Efficiency</option>
            <option value="maintenance">Maintenance Score</option>
          </select>
        </div>
        
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={analyticsData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey={selectedMetric} fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Efficiency Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, efficiency}) => `${name}: ${efficiency}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="efficiency"
              >
                {analyticsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Key Performance Indicators</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="font-medium">Total Capacity</span>
              <span className="text-xl font-bold text-green-600">382.3 kW</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="font-medium">Average Efficiency</span>
              <span className="text-xl font-bold text-blue-600">85.0%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
              <span className="font-medium">Maintenance Required</span>
              <span className="text-xl font-bold text-yellow-600">2 Sites</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <span className="font-medium">Energy Saved (CO₂)</span>
              <span className="text-xl font-bold text-purple-600">1.2T</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics