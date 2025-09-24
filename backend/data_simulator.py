import requests
import json
import time
import random
import math
from datetime import datetime, timedelta
import numpy as np

class SolarDataSimulator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.installations = [
            {
                'id': 'INST_001',
                'capacity_kw': 5.0,
                'location': 'Mumbai',
                'lat': 19.0760,
                'lon': 72.8777,
                'climatic_zone': 'tropical'
            },
            {
                'id': 'INST_002', 
                'capacity_kw': 50.0,
                'location': 'Delhi',
                'lat': 28.7041,
                'lon': 77.1025,
                'climatic_zone': 'semi-arid'
            },
            {
                'id': 'INST_003',
                'capacity_kw': 100.0,
                'location': 'Bangalore',
                'lat': 12.9716,
                'lon': 77.5946,
                'climatic_zone': 'tropical'
            }
        ]
    
    def get_realistic_solar_data(self, installation, current_time):
        """Generate realistic solar data based on time, location, and weather patterns"""
        
        # Time-based factors
        hour = current_time.hour
        month = current_time.month
        
        # Solar irradiation based on time of day and season
        if 6 <= hour <= 18:  # Daylight hours
            # Peak irradiation around noon
            time_factor = math.sin(math.pi * (hour - 6) / 12)
            
            # Seasonal variation (higher in winter months for India)
            seasonal_factor = 1.0
            if month in [11, 12, 1, 2]:  # Winter months
                seasonal_factor = 1.2
            elif month in [6, 7, 8, 9]:  # Monsoon months
                seasonal_factor = 0.7
            
            base_irradiation = 800 * time_factor * seasonal_factor
            
            # Add weather variability
            weather_factor = random.uniform(0.6, 1.0)
            irradiation = base_irradiation * weather_factor
            
        else:
            irradiation = 0
        
        # Temperature modeling
        base_temp = 25  # Base temperature
        if installation['climatic_zone'] == 'arid':
            base_temp = 30
        elif installation['climatic_zone'] == 'tropical':
            base_temp = 28
        
        # Daily temperature variation
        temp_variation = 10 * math.sin(math.pi * (hour - 6) / 12)
        ambient_temp = base_temp + temp_variation + random.uniform(-3, 3)
        
        # Module temperature (typically 20-30°C higher than ambient)
        module_temp = ambient_temp + 25 + (irradiation / 1000) * 15
        
        # PV power calculation
        if irradiation > 50:
            # Simplified PV power calculation
            efficiency = 0.85 - (module_temp - 25) * 0.004  # Temperature coefficient
            efficiency = max(0.7, efficiency)  # Minimum efficiency
            
            # Dust and soiling effects
            dust_level = random.uniform(0.1, 0.8)
            dust_factor = 1 - (dust_level * 0.3)  # Up to 30% loss due to dust
            
            pv_power = (irradiation / 1000) * installation['capacity_kw'] * efficiency * dust_factor
            
            # Add some realistic noise
            pv_power *= random.uniform(0.95, 1.05)
            pv_power = max(0, pv_power)
        else:
            pv_power = 0
            dust_level = random.uniform(0.1, 0.5)
        
        # Environmental factors
        wind_speed = random.uniform(1, 8)  # m/s
        humidity = random.uniform(40, 90)  # %
        
        # Inverter efficiency (can degrade over time)
        inverter_efficiency = random.uniform(92, 98)
        
        return {
            'installation_id': installation['id'],
            'timestamp': current_time.isoformat(),
            'pv_power_kw': round(pv_power, 3),
            'irradiation_wm2': round(irradiation, 1),
            'module_temp_c': round(module_temp, 1),
            'ambient_temp_c': round(ambient_temp, 1),
            'wind_speed_ms': round(wind_speed, 1),
            'humidity_percent': round(humidity, 1),
            'dust_level': round(dust_level, 2),
            'inverter_efficiency': round(inverter_efficiency, 1)
        }
    
    def send_telemetry_data(self, data):
        """Send telemetry data to the backend API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/telemetry",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ Data sent for {data['installation_id']}: {data['pv_power_kw']}kW")
                return True
            else:
                print(f"❌ Error sending data: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending telemetry: {str(e)}")
            return False
    
    def simulate_fault_conditions(self, data):
        """Simulate various fault conditions for testing alerts"""
        fault_type = random.choice(['normal', 'dust', 'temperature', 'inverter', 'shading'])
        
        if fault_type == 'dust':
            # High dust accumulation
            data['dust_level'] = random.uniform(0.8, 1.0)
            data['pv_power_kw'] *= 0.6  # Significant power loss
            
        elif fault_type == 'temperature':
            # Overheating
            data['module_temp_c'] = random.uniform(85, 95)
            data['pv_power_kw'] *= 0.8  # Power loss due to high temperature
            
        elif fault_type == 'inverter':
            # Inverter issues
            data['inverter_efficiency'] = random.uniform(75, 88)
            data['pv_power_kw'] *= 0.7  # Power loss due to inverter issues
            
        elif fault_type == 'shading':
            # Partial shading
            data['pv_power_kw'] *= random.uniform(0.3, 0.7)
            data['irradiation_wm2'] *= 0.5
        
        return data
    
    def run_simulation(self, duration_minutes=60, interval_seconds=30, include_faults=True):
        """Run the data simulation for specified duration"""
        print(f"🚀 Starting solar data simulation for {duration_minutes} minutes...")
        print(f"📊 Sending data every {interval_seconds} seconds")
        print(f"🏭 Simulating {len(self.installations)} installations")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        iteration = 0
        
        while datetime.now() < end_time:
            current_time = datetime.now()
            
            for installation in self.installations:
                # Generate realistic data
                data = self.get_realistic_solar_data(installation, current_time)
                
                # Occasionally simulate fault conditions (10% chance)
                if include_faults and random.random() < 0.1:
                    data = self.simulate_fault_conditions(data)
                    print(f"⚠️  Simulating fault condition for {installation['id']}")
                
                # Send data to backend
                self.send_telemetry_data(data)
            
            iteration += 1
            print(f"📈 Iteration {iteration} completed at {current_time.strftime('%H:%M:%S')}")
            
            # Wait for next iteration
            time.sleep(interval_seconds)
        
        print(f"✅ Simulation completed! Sent data for {duration_minutes} minutes")
    
    def send_historical_data(self, days_back=7):
        """Generate and send historical data for ML model training"""
        print(f"📚 Generating {days_back} days of historical data...")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        current_time = start_time
        
        while current_time < end_time:
            for installation in self.installations:
                data = self.get_realistic_solar_data(installation, current_time)
                
                # Add some historical variations
                if random.random() < 0.05:  # 5% chance of issues
                    data = self.simulate_fault_conditions(data)
                
                self.send_telemetry_data(data)
            
            # Move to next time point (every 15 minutes)
            current_time += timedelta(minutes=15)
        
        print(f"✅ Historical data generation completed!")

def main():
    simulator = SolarDataSimulator()
    
    print("Solar Energy Data Simulator")
    print("=" * 50)
    print("1. Send historical data (for ML training)")
    print("2. Start real-time simulation")
    print("3. Run both (recommended)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        days = int(input("Enter number of days of historical data (default 3): ") or "3")
        simulator.send_historical_data(days_back=days)
        
    elif choice == "2":
        duration = int(input("Enter simulation duration in minutes (default 60): ") or "60")
        interval = int(input("Enter data interval in seconds (default 30): ") or "30")
        simulator.run_simulation(duration_minutes=duration, interval_seconds=interval)
        
    elif choice == "3":
        print("Sending historical data first...")
        simulator.send_historical_data(days_back=2)
        
        print("\nStarting real-time simulation...")
        time.sleep(2)
        simulator.run_simulation(duration_minutes=30, interval_seconds=15)
        
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()