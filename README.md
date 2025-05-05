# Automatic Number Plate Recognition (ANPR) System

An advanced Automatic Number Plate Recognition system built with Python and YOLOv8, designed to detect and identify stolen vehicles from video feeds in real-time.

## Features

- **License Plate Detection & Recognition**

  - Utilizes YOLOv8 for accurate vehicle and license plate detection
  - Implements EasyOCR for high-quality text recognition from license plates
  - Handles various lighting conditions and angles

- **Stolen Vehicle Detection**

  - Maintains a SQLite database of stolen vehicles with detailed information
  - Real-time matching of detected plates against stolen vehicle database
  - Visual alerts and highlighting of matches

- **Vehicle Tracking**

  - SORT (Simple Online and Realtime Tracking) algorithm for consistent vehicle tracking across frames
  - Associates license plates with specific vehicles in multi-vehicle scenarios
  - Prevents duplicate detections of the same vehicle

- **Database Management**

  - Command-line tools for managing the stolen vehicle database
  - Add, update, and search for vehicles in the database
  - Import/export functionality via CSV files

- **Detection Logging**
  - Records all stolen vehicle detections with timestamps
  - Saves annotated frames as evidence
  - Comprehensive detection history and reporting

## System Requirements

- Python 3.8+
- CUDA-compatible GPU recommended for real-time performance

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/mohinik7/automatic-number-plate-recognition-python-yolov8.git
   cd automatic-number-plate-recognition-python-yolov8
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Initialize the database (already done by default):
   ```
   python database_utils.py
   ```

## Usage

### Processing Videos

Run license plate detection on a video file:

```
python main.py --video <video_path> --output <output_csv> --alert
```

Options:

- `--video`: Path to input video file
- `--output`: Path to save detection results CSV (default: test.csv)
- `--alert`: Enable console alerts for stolen vehicles
- `--no-frames`: Disable saving frames of stolen vehicles

### Managing Stolen Vehicles

Use the command-line interface to manage the stolen vehicle database:

```
# List all stolen vehicles
python manage_vehicles.py list

# Add a new stolen vehicle
python manage_vehicles.py add --license "AB12CDE" --make "Toyota" --model "Corolla" --year "2020" --color "Black" --description "Stolen in London" --date "2023-10-15"

# Update vehicle status
python manage_vehicles.py update --license "AB12CDE" --status "RECOVERED"

# Search for vehicles
python manage_vehicles.py search "Toyota"

# List all detection events
python manage_vehicles.py detections
```

### Import Vehicles from CSV

Import a list of stolen vehicles from a CSV file:

```
python database_utils.py stolen_vehicles.csv
```

The CSV should have the format: license_plate,make,model,year,color,description,date_reported

## How It Works

1. **Vehicle Detection**: YOLOv8 detects vehicles in each frame of the video
2. **License Plate Detection**: A specialized YOLOv8 model detects license plates within the vehicle regions
3. **OCR Processing**: EasyOCR extracts the text from the detected license plates
4. **Format Validation**: The system validates license plate formats and corrects common OCR errors
5. **Database Matching**: Detected license plates are checked against the stolen vehicle database
6. **Alert Generation**: Matches trigger alerts and frame captures
7. **Tracking**: The SORT algorithm ensures consistent tracking of vehicles across frames

## Project Structure

- `main.py`: Core video processing and detection script
- `util.py`: Utility functions for license plate processing
- `database_utils.py`: Database initialization and vehicle lookup functions
- `manage_vehicles.py`: Command-line interface for database management
- `reset_database.py`: Tool to reset the database to its initial state
- `models/`: Directory containing YOLOv8 models
- `output/`: Directory for saving detection frames
- `sort/`: SORT algorithm implementation for vehicle tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition
- [SORT](https://github.com/abewley/sort) for object tracking
