import requests
import json

def check_system_status():
    """Check if the entire system is running properly"""
    
    print("Solar Energy Management System - Status Check")
    print("=" * 50)
    
    # Check Backend
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("[OK] Backend API: RUNNING (Port 5000)")
        else:
            print("[ERROR] Backend API: ERROR")
    except:
        print("[ERROR] Backend API: NOT RUNNING")
    
    # Check Frontend
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("[OK] Frontend UI: RUNNING (Port 3000)")
        else:
            print("[ERROR] Frontend UI: ERROR")
    except:
        print("[ERROR] Frontend UI: NOT RUNNING")
    
    # Test API Endpoints
    print("\nTesting API Endpoints:")
    
    endpoints = [
        ('/api/installations', 'Installations'),
        ('/api/latest/INST_001', 'Telemetry Data'),
        ('/api/predictions/INST_001', 'ML Predictions'),
        ('/api/alerts/INST_001', 'Alert System'),
        ('/api/report/INST_001', 'AI Reports')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name}: Working")
            else:
                print(f"[ERROR] {name}: Error {response.status_code}")
        except:
            print(f"[ERROR] {name}: Connection Failed")
    
    print("\nSystem URLs:")
    print("Frontend Dashboard: http://localhost:3000")
    print("Backend API: http://localhost:5000/api/health")
    print("Reports Page: http://localhost:3000/reports")
    
    print("\nReady for Hackathon Demo!")

if __name__ == "__main__":
    check_system_status()