# ANPR Stolen Vehicle Detection System

An Automatic Number Plate Recognition (ANPR) system designed to detect and track stolen vehicles from video feeds.

## Features

- License plate detection and recognition using computer vision
- Real-time video processing from uploaded videos
- Stolen vehicle database management
- Automated alerts when stolen vehicles are detected
- Detection history and reporting
- User authentication and authorization
- Dashboard for vehicle and alert management

## System Architecture

### Components:

1. **Core ANPR Engine**

   - License plate detection using YOLOv8
   - OCR using EasyOCR
   - Vehicle tracking using SORT algorithm

2. **Database**

   - SQLite (development) / PostgreSQL (production - ready)
   - SQLAlchemy ORM

3. **Web Interface**
   - Flask web application
   - Bootstrap 5 responsive UI
   - User authentication with Flask-Login

## Tech Stack

- **Python:** Core language for the entire application
- **Flask:** Web framework
- **SQLAlchemy:** ORM for database operations
- **YOLOv8:** Object detection for vehicles
- **EasyOCR:** License plate text recognition
- **SORT:** Multiple object tracking
- **Bootstrap 5:** Frontend UI framework
- **SQLite:** Database (can be upgraded to PostgreSQL for production)

## Setup and Installation

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Required Python packages (see requirements.txt)

### Installation Steps

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/anpr-stolen-vehicle-detection.git
   cd anpr-stolen-vehicle-detection
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

4. Initialize the system:

   ```
   python run_all.py --reinit-db
   ```

5. Start the web server:

   ```
   python app.py
   ```

6. Access the web interface:

   ```
   http://127.0.0.1:5000
   ```

7. Login with default credentials:
   ```
   Username: admin
   Password: adminpassword
   ```

## Usage

### Processing Videos

1. Login to the system
2. Navigate to "Upload Video" in the sidebar
3. Upload a video file (MP4, AVI, MOV, MKV)
4. The system will process the video and detect any stolen vehicles
5. Notifications will appear if matches are found

### Managing Stolen Vehicles

1. Navigate to "Stolen Vehicles" in the sidebar
2. Add, edit, or delete vehicle records
3. Import/export vehicle data using CSV files

### Viewing Detections

1. Navigate to "Detections" to see all detected stolen vehicles
2. Click on any detection to see details, including the captured image
3. Export detection reports in CSV format

## Project Structure

- **app.py:** Main Flask application
- **main.py:** Core ANPR processing script
- **models.py:** Database models
- **database.py:** Database initialization and utilities
- **util.py:** Utility functions for ANPR
- **templates/:** HTML templates for web interface
- **static/:** Static assets (CSS, JS, images)
- **uploads/:** Directory for uploaded videos
- **models/:** Directory for ML models

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YOLOv8 by Ultralytics
- SORT (Simple Online and Realtime Tracking)
- EasyOCR for text recognition
- Flask and SQLAlchemy communities
