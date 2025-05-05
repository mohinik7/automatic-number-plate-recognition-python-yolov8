import sqlite3
import os
import csv
from datetime import datetime

# Database file path
DB_FILE = 'stolen_vehicles.db'

def initialize_database():
    """Initialize the database with required tables if they don't exist."""
    conn = None
    try:
        # Create database connection
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create stolen_vehicles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stolen_vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT UNIQUE,
            make TEXT,
            model TEXT,
            year TEXT,
            color TEXT,
            description TEXT,
            date_reported TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
        ''')
        
        # Create detections table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT,
            vehicle_id INTEGER,
            frame_number INTEGER,
            timestamp TEXT,
            confidence REAL,
            video_path TEXT,
            image_path TEXT,
            job_id TEXT,
            user_id TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES stolen_vehicles (id)
        )
        ''')
        
        conn.commit()
        print("Database initialized successfully")
        
        # If the database was just created, add sample data
        cursor.execute("SELECT COUNT(*) FROM stolen_vehicles")
        if cursor.fetchone()[0] == 0:
            add_sample_vehicles()
            
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def add_sample_vehicles():
    """Add sample stolen vehicles to the database."""
    sample_vehicles = [
        ('NA13NRU', 'Toyota', 'Corolla', '2018', 'Silver', 'Reported stolen in London', '2023-05-15'),
        ('XY34ZAB', 'Honda', 'Civic', '2020', 'Blue', 'Reported stolen in Manchester', '2023-06-22'),
        ('CD56EFG', 'BMW', '3 Series', '2019', 'Black', 'Reported stolen in Birmingham', '2023-07-03'),
        ('GH78IJK', 'Ford', 'Focus', '2017', 'Red', 'Reported stolen in Liverpool', '2023-08-12'),
        ('LM90NOP', 'Audi', 'A4', '2021', 'White', 'Reported stolen in Glasgow', '2023-09-18')
    ]
    
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.executemany('''
        INSERT INTO stolen_vehicles (license_plate, make, model, year, color, description, date_reported)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_vehicles)
        
        conn.commit()
        print(f"Added {len(sample_vehicles)} sample stolen vehicles to database")
    except Exception as e:
        print(f"Error adding sample vehicles: {e}")
    finally:
        if conn:
            conn.close()

def import_vehicles_from_csv(csv_file):
    """Import stolen vehicles from a CSV file."""
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            
            vehicles = []
            for row in csv_reader:
                if len(row) >= 7:
                    license_plate, make, model, year, color, description, date_reported = row[:7]
                    vehicles.append((license_plate, make, model, year, color, description, date_reported))
        
        cursor.executemany('''
        INSERT OR REPLACE INTO stolen_vehicles (license_plate, make, model, year, color, description, date_reported)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', vehicles)
        
        conn.commit()
        print(f"Imported {len(vehicles)} vehicles from {csv_file}")
        return True
    except Exception as e:
        print(f"Error importing vehicles from CSV: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_license_plate_in_database(license_plate):
    """
    Check if a license plate exists in the stolen vehicles database.
    
    Args:
        license_plate (str): The license plate to check
        
    Returns:
        dict: Vehicle information if found, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, license_plate, make, model, year, color, description, date_reported, status
        FROM stolen_vehicles
        WHERE license_plate = ? AND status = 'ACTIVE'
        ''', (license_plate,))
        
        row = cursor.fetchone()
        if row:
            vehicle = {
                'id': row[0],
                'license_plate': row[1],
                'make': row[2],
                'model': row[3],
                'year': row[4],
                'color': row[5],
                'description': row[6],
                'date_reported': row[7],
                'status': row[8]
            }
            return vehicle
        return None
    except Exception as e:
        print(f"Error checking license plate: {e}")
        return None
    finally:
        if conn:
            conn.close()

def record_detection_event(license_plate, vehicle_id, frame_number, timestamp, confidence, 
                         video_path, image_path=None, job_id=None, user_id=None):
    """
    Record a stolen vehicle detection event in the database.
    
    Args:
        license_plate (str): The detected license plate
        vehicle_id (int): The ID of the stolen vehicle
        frame_number (int): Frame number in the video
        timestamp (datetime): Detection timestamp
        confidence (float): Confidence score of the detection
        video_path (str): Path to the video file
        image_path (str, optional): Path to the saved frame image
        job_id (str, optional): Job identifier
        user_id (str, optional): User identifier
        
    Returns:
        int: ID of the recorded detection
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, datetime) else timestamp
        
        cursor.execute('''
        INSERT INTO detections 
        (license_plate, vehicle_id, frame_number, timestamp, confidence, video_path, image_path, job_id, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (license_plate, vehicle_id, frame_number, timestamp_str, confidence, 
              video_path, image_path, job_id, user_id))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error recording detection: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Fallback functions for direct access when not in Flask context
def fallback_check_license_plate(license_plate):
    """Fallback function to check license plate directly."""
    return check_license_plate_in_database(license_plate)

def fallback_record_detection(license_plate, vehicle_id, frame_number, timestamp, confidence, 
                            video_path, image_path=None, job_id=None, user_id=None):
    """Fallback function to record detection directly."""
    return record_detection_event(license_plate, vehicle_id, frame_number, timestamp, 
                                confidence, video_path, image_path, job_id, user_id)

# Initialize the database when the module is imported
initialize_database()

if __name__ == "__main__":
    # This allows the script to be run directly to initialize the database
    print("Initializing stolen vehicles database...")
    initialize_database()
    
    # Example command to import from CSV if provided as argument
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Importing vehicles from {csv_file}...")
        import_vehicles_from_csv(csv_file) 