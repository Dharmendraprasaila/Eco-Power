import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create PostgreSQL database for solar energy system"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("DROP DATABASE IF EXISTS solar_energy_db")
        cursor.execute("CREATE DATABASE solar_energy_db")
        
        print("Database 'solar_energy_db' created successfully!")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database and create extensions
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",
            port="5432",
            database="solar_energy_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create TimescaleDB extension for time-series data (if available)
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")
            print("TimescaleDB extension created!")
        except:
            print("TimescaleDB not available, using regular PostgreSQL")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

def insert_sample_data():
    """Insert sample installation data"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",
            port="5432",
            database="solar_energy_db"
        )
        cursor = conn.cursor()
        
        # Sample installations across different Indian climatic zones
        installations = [
            ('INST_001', 'Mumbai Residential', 'Mumbai, Maharashtra', 19.0760, 72.8777, 5.0, 20, 'tropical'),
            ('INST_002', 'Delhi Commercial', 'New Delhi, Delhi', 28.7041, 77.1025, 50.0, 200, 'semi-arid'),
            ('INST_003', 'Bangalore Tech Park', 'Bangalore, Karnataka', 12.9716, 77.5946, 100.0, 400, 'tropical'),
            ('INST_004', 'Chennai Industrial', 'Chennai, Tamil Nadu', 13.0827, 80.2707, 25.0, 100, 'tropical'),
            ('INST_005', 'Jaipur Solar Farm', 'Jaipur, Rajasthan', 26.9124, 75.7873, 200.0, 800, 'arid')
        ]
        
        for inst in installations:
            cursor.execute("""
                INSERT INTO solar_installations 
                (id, name, location, latitude, longitude, capacity_kw, panel_count, climatic_zone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, inst)
        
        conn.commit()
        print("Sample installation data inserted!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error inserting sample data: {str(e)}")
        return False

if __name__ == "__main__":
    print("Initializing Solar Energy Management Database...")
    
    if create_database():
        print("Database created successfully!")
        
        # Wait for Flask app to create tables, then insert sample data
        input("Press Enter after running Flask app to create tables...")
        
        if insert_sample_data():
            print("Sample data inserted successfully!")
        else:
            print("Failed to insert sample data")
    else:
        print("Failed to create database")