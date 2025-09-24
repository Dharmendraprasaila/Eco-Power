import requests
import time
import random
import math
from datetime import datetime

def generate_realistic_data(installation_id, capacity_kw):
    """Generate realistic solar data"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # Solar irradiation based on time of day
    if 6 <= hour <= 18:
        time_factor = math.sin(math.pi * (hour - 6) / 12)
        irradiation = 800 * time_factor * random.uniform(0.7, 1.0)
        
        # PV power calculation
        efficiency = random.uniform(0.8, 0.95)
        dust_factor = random.uniform(0.7, 1.0)
        pv_power = (irradiation / 1000) * capacity_kw * efficiency * dust_factor
    else:
        irradiation = 0
        pv_power = 0
    
    # Temperature modeling
    base_temp = 28 if installation_id == 'INST_001' else 30  # Mumbai vs Delhi
    temp_variation = 10 * math.sin(math.pi * (hour - 6) / 12) if hour >= 6 and hour <= 18 else 0
    ambient_temp = base_temp + temp_variation + random.uniform(-3, 3)
    module_temp = ambient_temp + 20 + (irradiation / 1000) * 15
    
    return {
        'installation_id': installation_id,
        'pv_power_kw': round(max(0, pv_power), 2),
        'irradiation_wm2': round(max(0, irradiation), 1),
        'module_temp_c': round(module_temp, 1),
        'ambient_temp_c': round(ambient_temp, 1),
        'wind_speed_ms': round(random.uniform(1, 8), 1),
        'humidity_percent': round(random.uniform(40, 90), 1),
        'dust_level': round(random.uniform(0.1, 0.8), 2),
        'inverter_efficiency': round(random.uniform(92, 98), 1)
    }

def send_telemetry(data):
    """Send telemetry data to backend"""
    try:
        response = requests.post(
            'http://localhost:5000/api/telemetry',
            json=data,
            timeout=5
        )
        if response.status_code == 201:
            print(f"✅ {data['installation_id']}: {data['pv_power_kw']}kW sent")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    installations = [
        ('INST_001', 5.0),   # Mumbai Residential
        ('INST_002', 50.0),  # Delhi Commercial  
        ('INST_003', 100.0), # Bangalore Tech Park
        ('INST_004', 25.0),  # Chennai Industrial
        ('INST_005', 200.0)  # Jaipur Solar Farm
    ]
    
    print("🚀 Starting Solar Data Simulator...")
    print("📊 Sending data every 10 seconds")
    print("🌞 Simulating realistic solar conditions")
    print("=" * 50)
    
    iteration = 0
    while True:
        try:
            iteration += 1
            print(f"\n📈 Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            
            for inst_id, capacity in installations:
                data = generate_realistic_data(inst_id, capacity)
                send_telemetry(data)
            
            print("⏱️  Waiting 10 seconds...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()