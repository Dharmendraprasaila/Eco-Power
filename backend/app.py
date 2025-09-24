from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import requests
import openai
import json
from apscheduler.schedulers.background import BackgroundScheduler
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration (using SQLite for quick demo)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///solar_energy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# OpenAI Configuration
openai.api_key = os.getenv('OPENAI_API_KEY', 'demo-key-for-testing')

# Weather API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class SolarInstallation(db.Model):
    __tablename__ = 'solar_installations'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity_kw = db.Column(db.Float, nullable=False)
    panel_count = db.Column(db.Integer, nullable=False)
    installation_date = db.Column(db.DateTime, default=datetime.utcnow)
    climatic_zone = db.Column(db.String(50), nullable=False)
    
class TelemetryData(db.Model):
    __tablename__ = 'telemetry_data'
    
    id = db.Column(db.Integer, primary_key=True)
    installation_id = db.Column(db.String(50), db.ForeignKey('solar_installations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pv_power_kw = db.Column(db.Float, nullable=False)
    irradiation_wm2 = db.Column(db.Float, nullable=False)
    module_temp_c = db.Column(db.Float, nullable=False)
    ambient_temp_c = db.Column(db.Float, nullable=False)
    wind_speed_ms = db.Column(db.Float, default=0)
    humidity_percent = db.Column(db.Float, default=0)
    dust_level = db.Column(db.Float, default=0)
    inverter_efficiency = db.Column(db.Float, default=95.0)

class PredictionData(db.Model):
    __tablename__ = 'prediction_data'
    
    id = db.Column(db.Integer, primary_key=True)
    installation_id = db.Column(db.String(50), db.ForeignKey('solar_installations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_power_kw = db.Column(db.Float, nullable=False)
    actual_power_kw = db.Column(db.Float)
    efficiency_score = db.Column(db.Float, nullable=False)
    maintenance_score = db.Column(db.Float, nullable=False)

class AlertData(db.Model):
    __tablename__ = 'alert_data'
    
    id = db.Column(db.Integer, primary_key=True)
    installation_id = db.Column(db.String(50), db.ForeignKey('solar_installations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, default=False)

# ML Model Class
class SolarPredictionModel:
    def __init__(self):
        self.power_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.efficiency_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, data):
        """Prepare features for ML model"""
        features = []
        for row in data:
            feature_row = [
                row.irradiation_wm2,
                row.module_temp_c,
                row.ambient_temp_c,
                row.wind_speed_ms,
                row.humidity_percent,
                row.dust_level,
                row.inverter_efficiency,
                row.timestamp.hour,
                row.timestamp.month,
                row.timestamp.weekday()
            ]
            features.append(feature_row)
        return np.array(features)
    
    def train_model(self, installation_id):
        """Train ML model with historical data"""
        try:
            # Get historical data
            historical_data = TelemetryData.query.filter_by(
                installation_id=installation_id
            ).order_by(TelemetryData.timestamp.desc()).limit(1000).all()
            
            if len(historical_data) < 50:
                logger.warning(f"Insufficient data for training: {len(historical_data)} records")
                return False
            
            # Prepare features and targets
            X = self.prepare_features(historical_data)
            y_power = [row.pv_power_kw for row in historical_data]
            
            # Calculate efficiency scores
            installation = SolarInstallation.query.get(installation_id)
            theoretical_power = []
            for row in historical_data:
                # Simplified theoretical power calculation
                theoretical = (row.irradiation_wm2 / 1000) * installation.capacity_kw * 0.85
                theoretical_power.append(theoretical)
            
            y_efficiency = [actual/theoretical if theoretical > 0 else 0 
                          for actual, theoretical in zip(y_power, theoretical_power)]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train models
            self.power_model.fit(X_scaled, y_power)
            self.efficiency_model.fit(X_scaled, y_efficiency)
            
            self.is_trained = True
            logger.info(f"Model trained successfully for installation {installation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def predict(self, telemetry_data):
        """Make predictions based on current telemetry"""
        if not self.is_trained:
            return None
        
        try:
            X = self.prepare_features([telemetry_data])
            X_scaled = self.scaler.transform(X)
            
            predicted_power = self.power_model.predict(X_scaled)[0]
            predicted_efficiency = self.efficiency_model.predict(X_scaled)[0]
            
            # Calculate maintenance score based on efficiency and environmental factors
            maintenance_score = self.calculate_maintenance_score(telemetry_data, predicted_efficiency)
            
            return {
                'predicted_power_kw': max(0, predicted_power),
                'efficiency_score': max(0, min(1, predicted_efficiency)),
                'maintenance_score': maintenance_score
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def calculate_maintenance_score(self, telemetry, efficiency):
        """Calculate maintenance score (0-100, higher means more maintenance needed)"""
        score = 0
        
        # Dust accumulation factor
        if telemetry.dust_level > 0.7:
            score += 30
        elif telemetry.dust_level > 0.5:
            score += 15
        
        # Temperature stress factor
        if telemetry.module_temp_c > 75:
            score += 25
        elif telemetry.module_temp_c > 65:
            score += 10
        
        # Efficiency degradation factor
        if efficiency < 0.8:
            score += 35
        elif efficiency < 0.9:
            score += 15
        
        # Inverter efficiency factor
        if telemetry.inverter_efficiency < 90:
            score += 20
        elif telemetry.inverter_efficiency < 95:
            score += 10
        
        return min(100, score)

# Initialize ML model
ml_model = SolarPredictionModel()

# Weather Service
class WeatherService:
    @staticmethod
    def get_weather_data(lat, lon):
        """Get current weather data from OpenWeatherMap"""
        try:
            url = f"{WEATHER_BASE_URL}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'irradiation': data.get('uvi', 5) * 100,  # Simplified irradiation calculation
                'weather_condition': data['weather'][0]['main']
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None
    
    @staticmethod
    def get_forecast_data(lat, lon, days=5):
        """Get weather forecast data"""
        try:
            url = f"{WEATHER_BASE_URL}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': WEATHER_API_KEY,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching forecast data: {str(e)}")
            return None

# Alert System
class AlertSystem:
    @staticmethod
    def check_performance_alerts(installation_id, telemetry, prediction):
        """Check for performance-related alerts"""
        alerts = []
        
        try:
            installation = SolarInstallation.query.get(installation_id)
            
            # Low power generation alert
            expected_power = (telemetry.irradiation_wm2 / 1000) * installation.capacity_kw * 0.85
            if telemetry.pv_power_kw < expected_power * 0.7:
                alerts.append({
                    'type': 'LOW_POWER',
                    'severity': 'HIGH',
                    'message': f'Power generation {telemetry.pv_power_kw:.2f}kW is significantly below expected {expected_power:.2f}kW'
                })
            
            # High temperature alert
            if telemetry.module_temp_c > 80:
                alerts.append({
                    'type': 'HIGH_TEMPERATURE',
                    'severity': 'MEDIUM',
                    'message': f'Module temperature {telemetry.module_temp_c}°C exceeds safe operating range'
                })
            
            # Dust accumulation alert
            if telemetry.dust_level > 0.8:
                alerts.append({
                    'type': 'DUST_ACCUMULATION',
                    'severity': 'MEDIUM',
                    'message': f'High dust level detected ({telemetry.dust_level:.1%}). Panel cleaning recommended'
                })
            
            # Inverter efficiency alert
            if telemetry.inverter_efficiency < 90:
                alerts.append({
                    'type': 'INVERTER_ISSUE',
                    'severity': 'HIGH',
                    'message': f'Inverter efficiency dropped to {telemetry.inverter_efficiency}%. Maintenance required'
                })
            
            # Maintenance alert based on ML prediction
            if prediction and prediction['maintenance_score'] > 70:
                alerts.append({
                    'type': 'MAINTENANCE_REQUIRED',
                    'severity': 'MEDIUM',
                    'message': f'Maintenance score: {prediction["maintenance_score"]:.0f}/100. Schedule preventive maintenance'
                })
            
            # Save alerts to database
            for alert in alerts:
                alert_record = AlertData(
                    installation_id=installation_id,
                    alert_type=alert['type'],
                    severity=alert['severity'],
                    message=alert['message']
                )
                db.session.add(alert_record)
            
            if alerts:
                db.session.commit()
                logger.info(f"Generated {len(alerts)} alerts for installation {installation_id}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            return []

# API Routes
@app.route('/api/installations', methods=['GET'])
def get_installations():
    """Get all solar installations"""
    try:
        installations = SolarInstallation.query.all()
        return jsonify([{
            'id': inst.id,
            'name': inst.name,
            'location': inst.location,
            'capacity_kw': inst.capacity_kw,
            'panel_count': inst.panel_count,
            'climatic_zone': inst.climatic_zone
        } for inst in installations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/installations', methods=['POST'])
def create_installation():
    """Create new solar installation"""
    try:
        data = request.get_json()
        
        installation = SolarInstallation(
            id=data['id'],
            name=data['name'],
            location=data['location'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            capacity_kw=data['capacity_kw'],
            panel_count=data['panel_count'],
            climatic_zone=data.get('climatic_zone', 'tropical')
        )
        
        db.session.add(installation)
        db.session.commit()
        
        return jsonify({'message': 'Installation created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/telemetry', methods=['POST'])
def ingest_telemetry():
    """Ingest real-time telemetry data"""
    try:
        data = request.get_json()
        
        # Create telemetry record
        telemetry = TelemetryData(
            installation_id=data['installation_id'],
            pv_power_kw=data['pv_power_kw'],
            irradiation_wm2=data['irradiation_wm2'],
            module_temp_c=data['module_temp_c'],
            ambient_temp_c=data['ambient_temp_c'],
            wind_speed_ms=data.get('wind_speed_ms', 0),
            humidity_percent=data.get('humidity_percent', 0),
            dust_level=data.get('dust_level', 0),
            inverter_efficiency=data.get('inverter_efficiency', 95.0)
        )
        
        db.session.add(telemetry)
        db.session.commit()
        
        # Process data synchronously for demo (in production, use Celery)
        process_telemetry_data(data['installation_id'], telemetry.id)
        
        return jsonify({'message': 'Telemetry data ingested successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest/<installation_id>', methods=['GET'])
def get_latest_telemetry(installation_id):
    """Get latest telemetry data for installation"""
    try:
        telemetry = TelemetryData.query.filter_by(
            installation_id=installation_id
        ).order_by(TelemetryData.timestamp.desc()).limit(50).all()
        
        return jsonify([{
            'timestamp': t.timestamp.isoformat(),
            'pv_power_kw': t.pv_power_kw,
            'irradiation_wm2': t.irradiation_wm2,
            'module_temp_c': t.module_temp_c,
            'ambient_temp_c': t.ambient_temp_c,
            'dust_level': t.dust_level,
            'inverter_efficiency': t.inverter_efficiency
        } for t in telemetry])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<installation_id>', methods=['GET'])
def get_predictions(installation_id):
    """Get latest predictions for installation"""
    try:
        predictions = PredictionData.query.filter_by(
            installation_id=installation_id
        ).order_by(PredictionData.timestamp.desc()).limit(10).all()
        
        return jsonify([{
            'timestamp': p.timestamp.isoformat(),
            'predicted_power_kw': p.predicted_power_kw,
            'actual_power_kw': p.actual_power_kw,
            'efficiency_score': p.efficiency_score,
            'maintenance_score': p.maintenance_score
        } for p in predictions])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/<installation_id>', methods=['GET'])
def get_alerts(installation_id):
    """Get alerts for installation"""
    try:
        alerts = AlertData.query.filter_by(
            installation_id=installation_id,
            resolved=False
        ).order_by(AlertData.timestamp.desc()).limit(20).all()
        
        return jsonify([{
            'id': a.id,
            'timestamp': a.timestamp.isoformat(),
            'alert_type': a.alert_type,
            'severity': a.severity,
            'message': a.message
        } for a in alerts])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<installation_id>', methods=['GET'])
def generate_report(installation_id):
    """Generate AI-powered performance report"""
    try:
        # Get installation data
        installation = SolarInstallation.query.get(installation_id)
        if not installation:
            return jsonify({'error': 'Installation not found'}), 404
        
        # Get recent telemetry and predictions
        telemetry = TelemetryData.query.filter_by(
            installation_id=installation_id
        ).order_by(TelemetryData.timestamp.desc()).limit(100).all()
        
        predictions = PredictionData.query.filter_by(
            installation_id=installation_id
        ).order_by(PredictionData.timestamp.desc()).limit(50).all()
        
        alerts = AlertData.query.filter_by(
            installation_id=installation_id,
            resolved=False
        ).all()
        
        # Prepare data for GPT
        report_data = {
            'installation': {
                'name': installation.name,
                'location': installation.location,
                'capacity_kw': installation.capacity_kw,
                'panel_count': installation.panel_count
            },
            'performance_summary': {
                'avg_power_kw': np.mean([t.pv_power_kw for t in telemetry]) if telemetry else 0,
                'avg_efficiency': np.mean([p.efficiency_score for p in predictions]) if predictions else 0,
                'maintenance_score': np.mean([p.maintenance_score for p in predictions]) if predictions else 0
            },
            'alerts_count': len(alerts),
            'recent_issues': [a.message for a in alerts[:5]]
        }
        
        # Generate report using GPT
        report = generate_ai_report(report_data)
        
        return jsonify({'report': report})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_report(data):
    """Generate AI-powered report using OpenAI GPT"""
    try:
        prompt = f"""
        Generate a comprehensive solar energy performance report for the following installation:
        
        Installation: {data['installation']['name']}
        Location: {data['installation']['location']}
        Capacity: {data['installation']['capacity_kw']} kW
        Panel Count: {data['installation']['panel_count']}
        
        Performance Summary:
        - Average Power Generation: {data['performance_summary']['avg_power_kw']:.2f} kW
        - Average Efficiency: {data['performance_summary']['avg_efficiency']:.1%}
        - Maintenance Score: {data['performance_summary']['maintenance_score']:.0f}/100
        
        Active Alerts: {data['alerts_count']}
        Recent Issues: {', '.join(data['recent_issues'])}
        
        Please provide:
        1. Performance Analysis
        2. Maintenance Recommendations
        3. Optimization Suggestions
        4. ROI Impact Assessment
        5. Next Steps
        
        Keep the report professional and actionable.
        """
        
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a solar energy expert providing technical analysis and recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating AI report: {str(e)}")
        return "Report generation failed. Please check API configuration."

# Background Tasks (using Celery would be better for production)
def process_telemetry_data(installation_id, telemetry_id):
    """Process telemetry data and generate predictions"""
    try:
        with app.app_context():
            telemetry = TelemetryData.query.get(telemetry_id)
            if not telemetry:
                return
            
            # Train model if not trained
            if not ml_model.is_trained:
                ml_model.train_model(installation_id)
            
            # Make prediction
            prediction = ml_model.predict(telemetry)
            if prediction:
                # Save prediction
                pred_record = PredictionData(
                    installation_id=installation_id,
                    predicted_power_kw=prediction['predicted_power_kw'],
                    actual_power_kw=telemetry.pv_power_kw,
                    efficiency_score=prediction['efficiency_score'],
                    maintenance_score=prediction['maintenance_score']
                )
                db.session.add(pred_record)
                
                # Check for alerts
                AlertSystem.check_performance_alerts(installation_id, telemetry, prediction)
                
                db.session.commit()
                
    except Exception as e:
        logger.error(f"Error processing telemetry data: {str(e)}")

# Scheduler for periodic tasks
scheduler = BackgroundScheduler()

def update_weather_data():
    """Update weather data for all installations"""
    try:
        with app.app_context():
            installations = SolarInstallation.query.all()
            for installation in installations:
                weather_data = WeatherService.get_weather_data(
                    installation.latitude, 
                    installation.longitude
                )
                if weather_data:
                    # Create synthetic telemetry with weather data
                    telemetry = TelemetryData(
                        installation_id=installation.id,
                        pv_power_kw=0,  # Will be updated with real data
                        irradiation_wm2=weather_data['irradiation'],
                        module_temp_c=weather_data['temperature'] + 20,  # Module temp is higher
                        ambient_temp_c=weather_data['temperature'],
                        wind_speed_ms=weather_data['wind_speed'],
                        humidity_percent=weather_data['humidity']
                    )
                    # This would be replaced with real sensor data in production
                    
    except Exception as e:
        logger.error(f"Error updating weather data: {str(e)}")

# Schedule periodic tasks
scheduler.add_job(
    func=update_weather_data,
    trigger="interval",
    minutes=15,
    id='weather_update'
)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'ml_model_trained': ml_model.is_trained
    })

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        # Insert sample installations if they don't exist
        if SolarInstallation.query.count() == 0:
            sample_installations = [
                SolarInstallation(
                    id='INST_001',
                    name='Mumbai Residential',
                    location='Mumbai, Maharashtra',
                    latitude=19.0760,
                    longitude=72.8777,
                    capacity_kw=5.0,
                    panel_count=20,
                    climatic_zone='tropical'
                ),
                SolarInstallation(
                    id='INST_002',
                    name='Delhi Commercial',
                    location='New Delhi, Delhi',
                    latitude=28.7041,
                    longitude=77.1025,
                    capacity_kw=50.0,
                    panel_count=200,
                    climatic_zone='semi-arid'
                ),
                SolarInstallation(
                    id='INST_003',
                    name='Bangalore Tech Park',
                    location='Bangalore, Karnataka',
                    latitude=12.9716,
                    longitude=77.5946,
                    capacity_kw=100.0,
                    panel_count=400,
                    climatic_zone='tropical'
                )
            ]
            
            for installation in sample_installations:
                db.session.add(installation)
            
            db.session.commit()
            print("Sample installations added!")

if __name__ == '__main__':
    # Create tables on startup
    create_tables()
    
    # Start scheduler
    scheduler.start()
    
    print("🚀 Solar Energy Management System Backend Started!")
    print("📊 API available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)