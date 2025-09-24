from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime, timedelta
import random
import math

app = Flask(__name__)
CORS(app)

# In-memory storage for demo
installations = [
    {
        'id': 'INST_001',
        'name': 'Mumbai Residential',
        'location': 'Mumbai, Maharashtra',
        'capacity_kw': 5.0,
        'panel_count': 20,
        'climatic_zone': 'tropical'
    },
    {
        'id': 'INST_002',
        'name': 'Delhi Commercial',
        'location': 'New Delhi, Delhi',
        'capacity_kw': 50.0,
        'panel_count': 200,
        'climatic_zone': 'semi-arid'
    },
    {
        'id': 'INST_003',
        'name': 'Bangalore Tech Park',
        'location': 'Bangalore, Karnataka',
        'capacity_kw': 100.0,
        'panel_count': 400,
        'climatic_zone': 'tropical'
    },
    {
        'id': 'INST_004',
        'name': 'Chennai Industrial',
        'location': 'Chennai, Tamil Nadu',
        'capacity_kw': 25.0,
        'panel_count': 100,
        'climatic_zone': 'tropical'
    },
    {
        'id': 'INST_005',
        'name': 'Jaipur Solar Farm',
        'location': 'Jaipur, Rajasthan',
        'capacity_kw': 200.0,
        'panel_count': 800,
        'climatic_zone': 'arid'
    }
]

telemetry_data = {}
predictions_data = {}
alerts_data = {}

def generate_sample_data(installation_id):
    """Generate realistic sample data"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # Generate realistic solar data based on time
    if 6 <= hour <= 18:
        time_factor = math.sin(math.pi * (hour - 6) / 12)
        irradiation = 800 * time_factor * random.uniform(0.7, 1.0)
        
        installation = next(i for i in installations if i['id'] == installation_id)
        capacity = installation['capacity_kw']
        
        efficiency = random.uniform(0.8, 0.95)
        pv_power = (irradiation / 1000) * capacity * efficiency
    else:
        irradiation = 0
        pv_power = 0
    
    ambient_temp = 25 + 10 * math.sin(math.pi * (hour - 6) / 12) + random.uniform(-3, 3)
    module_temp = ambient_temp + 20 + (irradiation / 1000) * 15
    
    return {
        'timestamp': current_time.isoformat(),
        'pv_power_kw': round(pv_power, 2),
        'irradiation_wm2': round(irradiation, 1),
        'module_temp_c': round(module_temp, 1),
        'ambient_temp_c': round(ambient_temp, 1),
        'wind_speed_ms': round(random.uniform(1, 8), 1),
        'humidity_percent': round(random.uniform(40, 90), 1),
        'dust_level': round(random.uniform(0.1, 0.8), 2),
        'inverter_efficiency': round(random.uniform(92, 98), 1)
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Solar Energy Management System API is running!'
    })

@app.route('/api/installations', methods=['GET'])
def get_installations():
    return jsonify(installations)

@app.route('/api/telemetry', methods=['POST'])
def ingest_telemetry():
    try:
        data = request.get_json()
        installation_id = data['installation_id']
        
        if installation_id not in telemetry_data:
            telemetry_data[installation_id] = []
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        telemetry_data[installation_id].append(data)
        
        # Keep only last 100 records
        telemetry_data[installation_id] = telemetry_data[installation_id][-100:]
        
        # Generate prediction
        prediction = {
            'timestamp': data['timestamp'],
            'predicted_power_kw': data['pv_power_kw'] * random.uniform(0.95, 1.05),
            'actual_power_kw': data['pv_power_kw'],
            'efficiency_score': random.uniform(0.8, 0.95),
            'maintenance_score': random.uniform(10, 80)
        }
        
        if installation_id not in predictions_data:
            predictions_data[installation_id] = []
        predictions_data[installation_id].append(prediction)
        predictions_data[installation_id] = predictions_data[installation_id][-50:]
        
        # Generate alerts if needed
        if data['pv_power_kw'] < 1.0 and data['irradiation_wm2'] > 500:
            alert = {
                'id': len(alerts_data.get(installation_id, [])) + 1,
                'timestamp': data['timestamp'],
                'alert_type': 'LOW_POWER',
                'severity': 'HIGH',
                'message': f'Low power generation detected: {data["pv_power_kw"]}kW with high irradiation'
            }
            
            if installation_id not in alerts_data:
                alerts_data[installation_id] = []
            alerts_data[installation_id].append(alert)
        
        if data.get('dust_level', 0) > 0.7:
            alert = {
                'id': len(alerts_data.get(installation_id, [])) + 1,
                'timestamp': data['timestamp'],
                'alert_type': 'DUST_ACCUMULATION',
                'severity': 'MEDIUM',
                'message': f'High dust level detected: {data["dust_level"]:.1%}. Panel cleaning recommended'
            }
            
            if installation_id not in alerts_data:
                alerts_data[installation_id] = []
            alerts_data[installation_id].append(alert)
        
        return jsonify({'message': 'Telemetry data ingested successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest/<installation_id>', methods=['GET'])
def get_latest_telemetry(installation_id):
    try:
        # If no data exists, generate some sample data
        if installation_id not in telemetry_data or len(telemetry_data[installation_id]) == 0:
            sample_data = []
            for i in range(20):
                data = generate_sample_data(installation_id)
                # Adjust timestamp for historical data
                past_time = datetime.now() - timedelta(minutes=i*5)
                data['timestamp'] = past_time.isoformat()
                sample_data.append(data)
            
            telemetry_data[installation_id] = sample_data
        
        return jsonify(telemetry_data[installation_id][-50:])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<installation_id>', methods=['GET'])
def get_predictions(installation_id):
    try:
        if installation_id not in predictions_data:
            # Generate sample predictions
            sample_predictions = []
            for i in range(10):
                past_time = datetime.now() - timedelta(minutes=i*10)
                prediction = {
                    'timestamp': past_time.isoformat(),
                    'predicted_power_kw': random.uniform(1, 50),
                    'actual_power_kw': random.uniform(1, 50),
                    'efficiency_score': random.uniform(0.8, 0.95),
                    'maintenance_score': random.uniform(10, 80)
                }
                sample_predictions.append(prediction)
            
            predictions_data[installation_id] = sample_predictions
        
        return jsonify(predictions_data[installation_id])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<installation_id>', methods=['GET'])
def get_alerts(installation_id):
    try:
        if installation_id not in alerts_data:
            # Generate sample alerts
            sample_alerts = [
                {
                    'id': 1,
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': 'DUST_ACCUMULATION',
                    'severity': 'MEDIUM',
                    'message': 'Panel cleaning recommended due to dust accumulation'
                },
                {
                    'id': 2,
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'alert_type': 'HIGH_TEMPERATURE',
                    'severity': 'LOW',
                    'message': 'Module temperature slightly elevated'
                }
            ]
            alerts_data[installation_id] = sample_alerts
        
        return jsonify(alerts_data[installation_id])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<installation_id>', methods=['GET'])
def generate_report(installation_id):
    try:
        installation = next((i for i in installations if i['id'] == installation_id), None)
        if not installation:
            return jsonify({'error': 'Installation not found'}), 404
        
        # Generate a comprehensive report
        report = f"""
SOLAR ENERGY PERFORMANCE REPORT
===============================

Installation: {installation['name']}
Location: {installation['location']}
Capacity: {installation['capacity_kw']} kW
Climate Zone: {installation['climatic_zone']}

PERFORMANCE ANALYSIS
-------------------
* Current system is operating within normal parameters
* Average efficiency: 87.5% (Good)
* Peak power generation: {installation['capacity_kw'] * 0.9:.1f} kW
* Operating temperature: Normal range

MAINTENANCE RECOMMENDATIONS
--------------------------
* Panel Cleaning: Recommended every 2-3 weeks during dry season
* Inverter Check: Schedule quarterly maintenance
* Performance Optimization: Consider angle adjustment for winter months

ROI ANALYSIS
-----------
* Monthly Energy Savings: Rs.{installation['capacity_kw'] * 150:.0f}
* Payback Period: 6.2 years (Excellent)
* CO2 Reduction: {installation['capacity_kw'] * 1.2:.1f} tons/year

NEXT STEPS
----------
1. Schedule panel cleaning within 1 week
2. Monitor dust accumulation levels
3. Consider battery storage integration
4. Plan for monsoon season adjustments

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Status: HEALTHY
        """
        
        return jsonify({'report': report.strip()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Solar Energy Management System Backend Started!")
    print("API available at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("Frontend should connect to: http://localhost:3000")
    print("Ready for 5-hour hackathon demo!")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)