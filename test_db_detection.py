from database_utils import check_license_plate_in_database, record_detection_event
from datetime import datetime
import sys

def test_db_detection():
    """
    Test the database detection functionality.
    """
    print("Testing database functionality for license plate detection")
    
    # Get the license plate from command line or use a default
    if len(sys.argv) > 1:
        license_plate = sys.argv[1]
    else:
        # Use one of the license plates we added to the database
        license_plate = "NA13NRU"  # Toyota Corolla
    
    print(f"Checking if license plate '{license_plate}' is in the stolen vehicles database...")
    
    # Check if the license plate is in the database
    vehicle = check_license_plate_in_database(license_plate)
    
    if vehicle:
        print("\n⚠️ STOLEN VEHICLE DETECTED ⚠️")
        print(f"License: {license_plate}")
        print(f"Vehicle Info: {vehicle.get('year', 'N/A')} " +
              f"{vehicle.get('make', 'N/A')} " +
              f"{vehicle.get('model', 'N/A')} " +
              f"({vehicle.get('color', 'N/A')})")
        print(f"Description: {vehicle.get('description', 'N/A')}")
        print("-" * 50)
        
        # Record the detection (simulating detection in a video)
        detection_time = datetime.now()
        detection_id = record_detection_event(
            license_plate=license_plate,
            vehicle_id=vehicle.get('id'),
            frame_number=100,  # Simulated frame number
            timestamp=detection_time,
            confidence=0.95,  # Simulated confidence score
            video_path="sample2.mp4",  # Simulated video path
            image_path=None
        )
        
        if detection_id:
            print(f"Detection recorded successfully with ID: {detection_id}")
        else:
            print("Failed to record detection event.")
    else:
        print(f"License plate '{license_plate}' not found in stolen vehicles database.")
        print("Try one of these plates from our database:")
        print("NA13NRU, ML51VSU, GY15OGJ, NA54KGJ")

if __name__ == "__main__":
    test_db_detection() 