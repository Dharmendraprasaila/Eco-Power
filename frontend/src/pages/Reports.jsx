import React, { useState } from 'react'
import { FileText, Download, Calendar, BarChart3 } from 'lucide-react'

const Reports = () => {
  const [selectedInstallation, setSelectedInstallation] = useState('INST_001')
  const [reportType, setReportType] = useState('performance')
  const [loading, setLoading] = useState(false)

  const generateReport = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/report/${selectedInstallation}`)
      if (response.ok) {
        const data = await response.json()
        
        // Create and download report
        const reportWindow = window.open('', '_blank')
        reportWindow.document.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>Solar Performance Report - ${selectedInstallation}</title>
              <style>
                body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
                .header { border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; }
                .section { margin: 20px 0; }
                .highlight { background-color: #f0f9ff; padding: 10px; border-left: 4px solid #2563eb; }
                pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
              </style>
            </head>
            <body>
              <div class="header">
                <h1>🌞 Solar Energy Performance Report</h1>
                <p>Installation ID: ${selectedInstallation}</p>
                <p>Generated: ${new Date().toLocaleString()}</p>
              </div>
              
              <div class="section">
                <pre>${data.report}</pre>
              </div>
              
              <div class="section">
                <p><em>This report was generated using AI-powered analysis of your solar installation data.</em></p>
              </div>
            </body>
          </html>
        `)
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const reportTypes = [
    { value: 'performance', label: 'Performance Analysis', icon: BarChart3 },
    { value: 'maintenance', label: 'Maintenance Report', icon: FileText },
    { value: 'roi', label: 'ROI Analysis', icon: Calendar },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI-Powered Reports</h1>
        <p className="text-gray-600">Generate intelligent insights and recommendations</p>
      </div>

      {/* Report Generation Form */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Generate New Report</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Installation
            </label>
            <select 
              value={selectedInstallation}
              onChange={(e) => setSelectedInstallation(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="INST_001">Mumbai Residential (5kW)</option>
              <option value="INST_002">Delhi Commercial (50kW)</option>
              <option value="INST_003">Bangalore Tech Park (100kW)</option>
              <option value="INST_004">Chennai Industrial (25kW)</option>
              <option value="INST_005">Jaipur Solar Farm (200kW)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Type
            </label>
            <select 
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {reportTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button 
              onClick={generateReport}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <FileText className="h-4 w-4 mr-2" />
              )}
              {loading ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>
      </div>

      {/* Report Templates */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reportTypes.map(type => {
          const IconComponent = type.icon
          return (
            <div key={type.value} className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
              <div className="flex items-center mb-4">
                <IconComponent className="h-6 w-6 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold">{type.label}</h3>
              </div>
              
              <div className="text-sm text-gray-600 space-y-2">
                {type.value === 'performance' && (
                  <ul className="list-disc list-inside space-y-1">
                    <li>Power generation analysis</li>
                    <li>Efficiency trends</li>
                    <li>Weather impact assessment</li>
                    <li>Performance benchmarking</li>
                  </ul>
                )}
                
                {type.value === 'maintenance' && (
                  <ul className="list-disc list-inside space-y-1">
                    <li>Predictive maintenance alerts</li>
                    <li>Component health status</li>
                    <li>Cleaning schedule recommendations</li>
                    <li>Repair priority matrix</li>
                  </ul>
                )}
                
                {type.value === 'roi' && (
                  <ul className="list-disc list-inside space-y-1">
                    <li>Financial performance metrics</li>
                    <li>Energy savings calculation</li>
                    <li>Payback period analysis</li>
                    <li>Future projections</li>
                  </ul>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Reports */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Recent Reports</h3>
        
        <div className="space-y-3">
          {[
            { name: 'Performance Analysis - Mumbai Residential', date: '2024-01-15', type: 'Performance' },
            { name: 'Maintenance Report - Delhi Commercial', date: '2024-01-14', type: 'Maintenance' },
            { name: 'ROI Analysis - Bangalore Tech Park', date: '2024-01-13', type: 'ROI' },
          ].map((report, index) => (
            <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">{report.name}</p>
                  <p className="text-sm text-gray-500">{report.date} • {report.type}</p>
                </div>
              </div>
              
              <button className="text-blue-600 hover:text-blue-800 flex items-center">
                <Download className="h-4 w-4 mr-1" />
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Reports