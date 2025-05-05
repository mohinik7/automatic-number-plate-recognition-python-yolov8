import sqlite3
import argparse
from tabulate import tabulate as tabulate_fn

DB_FILE = 'stolen_vehicles.db'

def list_all_vehicles():
    """List all stolen vehicles in the database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, license_plate, make, model, year, color, description, date_reported, status
        FROM stolen_vehicles
        ORDER BY date_reported DESC
        ''')
        
        rows = cursor.fetchall()
        headers = ['ID', 'License Plate', 'Make', 'Model', 'Year', 'Color', 'Description', 'Date Reported', 'Status']
        
        if rows:
            print(tabulate_fn(rows, headers=headers, tablefmt='grid'))
            print(f"Total: {len(rows)} vehicles")
        else:
            print("No stolen vehicles found in the database.")
            
    except Exception as e:
        print(f"Error listing vehicles: {e}")
    finally:
        if conn:
            conn.close()

def add_vehicle(license_plate, make, model, year, color, description, date_reported):
    """Add a new stolen vehicle to the database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if license plate already exists
        cursor.execute("SELECT id FROM stolen_vehicles WHERE license_plate = ?", (license_plate,))
        if cursor.fetchone():
            print(f"Vehicle with license plate '{license_plate}' already exists in the database.")
            return False
        
        cursor.execute('''
        INSERT INTO stolen_vehicles (license_plate, make, model, year, color, description, date_reported)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (license_plate, make, model, year, color, description, date_reported))
        
        conn.commit()
        print(f"Added vehicle with license plate '{license_plate}' to the database.")
        return True
    except Exception as e:
        print(f"Error adding vehicle: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_vehicle_status(license_plate, status):
    """Update the status of a stolen vehicle."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM stolen_vehicles WHERE license_plate = ?", (license_plate,))
        if not cursor.fetchone():
            print(f"No vehicle found with license plate '{license_plate}'.")
            return False
        
        cursor.execute('''
        UPDATE stolen_vehicles SET status = ? WHERE license_plate = ?
        ''', (status, license_plate))
        
        conn.commit()
        print(f"Updated status of vehicle '{license_plate}' to '{status}'.")
        return True
    except Exception as e:
        print(f"Error updating vehicle status: {e}")
        return False
    finally:
        if conn:
            conn.close()

def search_vehicles(search_term):
    """Search for vehicles matching the given term."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Search across multiple fields
        cursor.execute('''
        SELECT id, license_plate, make, model, year, color, description, date_reported, status
        FROM stolen_vehicles
        WHERE license_plate LIKE ? OR make LIKE ? OR model LIKE ? OR color LIKE ? OR description LIKE ?
        ORDER BY date_reported DESC
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        headers = ['ID', 'License Plate', 'Make', 'Model', 'Year', 'Color', 'Description', 'Date Reported', 'Status']
        
        if rows:
            print(f"Search results for '{search_term}':")
            print(tabulate_fn(rows, headers=headers, tablefmt='grid'))
            print(f"Total: {len(rows)} vehicles")
        else:
            print(f"No vehicles found matching '{search_term}'.")
            
    except Exception as e:
        print(f"Error searching vehicles: {e}")
    finally:
        if conn:
            conn.close()

def list_detections():
    """List all detection events."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT d.id, d.license_plate, v.make, v.model, d.frame_number, 
               d.timestamp, d.confidence, d.video_path, d.image_path
        FROM detections d
        JOIN stolen_vehicles v ON d.vehicle_id = v.id
        ORDER BY d.timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        headers = ['ID', 'License Plate', 'Make', 'Model', 'Frame', 'Timestamp', 
                   'Confidence', 'Video Path', 'Image Path']
        
        if rows:
            print(tabulate_fn(rows, headers=headers, tablefmt='grid'))
            print(f"Total: {len(rows)} detections")
        else:
            print("No detection events found in the database.")
            
    except Exception as e:
        print(f"Error listing detections: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage stolen vehicles database')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all stolen vehicles')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new stolen vehicle')
    add_parser.add_argument('--license', required=True, help='License plate number')
    add_parser.add_argument('--make', required=True, help='Vehicle make')
    add_parser.add_argument('--model', required=True, help='Vehicle model')
    add_parser.add_argument('--year', required=True, help='Vehicle year')
    add_parser.add_argument('--color', required=True, help='Vehicle color')
    add_parser.add_argument('--description', required=True, help='Theft description')
    add_parser.add_argument('--date', required=True, help='Date reported (YYYY-MM-DD)')
    
    # Update status command
    update_parser = subparsers.add_parser('update', help='Update vehicle status')
    update_parser.add_argument('--license', required=True, help='License plate number')
    update_parser.add_argument('--status', required=True, choices=['ACTIVE', 'RECOVERED', 'INVALID'], 
                              help='New status')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for vehicles')
    search_parser.add_argument('term', help='Search term')
    
    # Detections command
    detections_parser = subparsers.add_parser('detections', help='List all detection events')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_all_vehicles()
    elif args.command == 'add':
        add_vehicle(args.license, args.make, args.model, args.year, 
                   args.color, args.description, args.date)
    elif args.command == 'update':
        update_vehicle_status(args.license, args.status)
    elif args.command == 'search':
        search_vehicles(args.term)
    elif args.command == 'detections':
        list_detections()
    else:
        parser.print_help() 