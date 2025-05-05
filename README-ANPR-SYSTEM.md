# ANPR Stolen Vehicle Detection System

An Automatic Number Plate Recognition (ANPR) system designed to detect and track stolen vehicles from video feeds.

## Features

- License plate detection and recognition using computer vision
- Real-time video processing from uploaded videos
- Stolen vehicle database management
- Automated alerts when stolen vehicles are detected
- Sightings history and reporting
- User authentication and authorization
- Dashboard for vehicle and alert management

## System Architecture

The system builds upon an existing ANPR project, adding a database for stolen vehicles, alert functionalities, and a web interface.

### Components:

1. **Core ANPR Engine**

   - License plate detection using YOLOv8
   - OCR using EasyOCR
   - Vehicle tracking using SORT algorithm

2. **Database**

   - SQLite (development) / PostgreSQL (production)
   - Stores stolen vehicle information
   - Records detection events
   - Manages users and authentication

3. **Web Interface**
   - Flask-based web application
   - Dashboard for system monitoring
   - Upload and process videos
   - Manage stolen vehicle database
   - View detection history and alerts

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/anpr-stolen-vehicle-detection.git
   cd anpr-stolen-vehicle-detection
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python seed_data.py
   ```

## Running the Application

1. Start the Flask web server:

   ```
   python app.py
   ```

2. Access the web interface at `http://localhost:5000`

3. Login with default credentials:
   - Username: admin
   - Password: adminpassword

## Processing Videos from Command Line

You can also process videos directly using the command line:

```
python main.py --video path/to/video.mp4 --output results.csv
```

Additional options:

- `--no-alerts`: Disable console alerts for stolen vehicles
- `--no-frames`: Disable saving frames of stolen vehicles

## Development

### Project Structure

```
.
├── app.py                  # Main Flask application
├── database.py             # Database connection and utilities
├── main.py                 # Core ANPR processing
├── models.py               # SQLAlchemy models
├── seed_data.py            # Database seeding script
├── util.py                 # Utility functions for ANPR
├── templates/              # Jinja2 templates
│   ├── layout.html         # Base template
│   ├── index.html          # Landing page
│   ├── login.html          # Login form
│   ├── dashboard.html      # Dashboard
│   └── ...
├── static/                 # Static assets
├── uploads/                # Video upload directory
└── output/                 # Detection output directory
    └── frames/             # Saved detection frames
```

### Database Schema

- **users**: Authentication and user management
- **stolen_vehicles**: Stolen vehicle registry
- **detection_events**: Records of stolen vehicle sightings
- **video_processing_jobs**: Status tracking for video processing

## License

[MIT License](LICENSE)
