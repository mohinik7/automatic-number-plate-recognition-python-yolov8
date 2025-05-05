import sqlite3
import os
from database_utils import import_vehicles_from_csv

DB_FILE = 'stolen_vehicles.db'
CSV_FILE = 'stolen_vehicles.csv'

def reset_database():
    """Reset the database by dropping and recreating tables."""
    print("Resetting the stolen vehicles database...")
    
    # Remove old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database file: {DB_FILE}")
    
    # Create a new database connection
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
    conn.close()
    
    print("Database reset complete. Tables recreated.")
    
    # Import vehicles from CSV
    if os.path.exists(CSV_FILE):
        print(f"Importing vehicles from {CSV_FILE}...")
        import_vehicles_from_csv(CSV_FILE)
    else:
        print(f"CSV file not found: {CSV_FILE}")

if __name__ == "__main__":
    reset_database() 