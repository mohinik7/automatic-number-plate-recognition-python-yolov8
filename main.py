import torch
from ultralytics import YOLO
import cv2
import os
import argparse
import numpy as np
from datetime import datetime
import traceback

import util
from sort.sort import *
from util import get_car, read_license_plate, write_csv

# Add YOLO classes to the safe globals list to allow loading the models
# Commented out because this function is not available in older PyTorch versions
# torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])

# Try importing database utilities - will work in Flask context but can still function without it
try:
    from database_utils import check_license_plate_in_database, record_detection_event, fallback_check_license_plate, fallback_record_detection
    HAVE_DB_UTILS = True
except ImportError:
    print("Warning: database_utils not available, running without database functionality")
    HAVE_DB_UTILS = False

def process_video(video_path, output_path='./test.csv', user_id=None, job_id=None, save_detections=True, 
                  alert_on_match=False, save_frames=True, frames_output_dir='./output/frames'):
    """
    Process a video file, detect license plates, and check against stolen vehicle database
    
    Args:
        video_path (str): Path to the video file
        output_path (str): Path to save the output CSV
        user_id (int, optional): ID of the user processing the video
        job_id (int, optional): ID of the job processing the video
        save_detections (bool): Whether to save detection data to CSV
        alert_on_match (bool): Whether to print alerts when stolen vehicles are found (default: False)
        save_frames (bool): Whether to save frames with detected stolen vehicles
        frames_output_dir (str): Directory to save detection frames
    
    Returns:
        list: List of detection dictionaries for stolen vehicles
    """
    results = {}
    detection_results = []
    
    # Create directories if they don't exist
    if save_frames and not os.path.exists(frames_output_dir):
        os.makedirs(frames_output_dir, exist_ok=True)
    
    mot_tracker = Sort()
    
    # Download models if they don't exist
    if not os.path.exists('yolov8n.pt'):
        print("Downloading YOLOv8n model...")
        # Using torch.hub to download the model
        torch.hub.download_url_to_file('https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt', 'yolov8n.pt')
    
    if not os.path.exists('./models/license_plate_detector.pt'):
        print("Error: License plate detector model not found.")
        print("Please make sure the model exists at ./models/license_plate_detector.pt")
        return []
    
    # load models
    try:
        coco_model = YOLO('yolov8n.pt')
        license_plate_detector = YOLO('./models/license_plate_detector.pt')
    except Exception as e:
        print(f"Error loading models: {e}")
        traceback.print_exc()
        return []
    
    # load video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video file: {video_path}")
        return []
    
    # Get video properties for timestamp calculation
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Vehicle classes in COCO dataset: car(2), motorcycle(3), bus(5), truck(7)
    vehicles = [2, 3, 5, 7]
    
    # Track unique license plates to avoid duplicate detections
    detected_license_plates = set()
    
    # read frames
    frame_nmr = -1
    ret = True
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret:
            results[frame_nmr] = {}
            # detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])
    
            # track vehicles
            track_ids = mot_tracker.update(np.asarray(detections_))
    
            # detect license plates
            license_plates = license_plate_detector(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate
    
                # assign license plate to car
                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
    
                if car_id != -1:
                    # crop license plate
                    license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
    
                    # process license plate
                    license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                    _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
    
                    # read license plate number
                    license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
    
                    if license_plate_text is not None:
                        # Store in results dictionary
                        results[frame_nmr][car_id] = {
                            'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                            'license_plate': {
                                'bbox': [x1, y1, x2, y2],
                                'text': license_plate_text,
                                'bbox_score': score,
                                'text_score': license_plate_text_score
                            }
                        }
                        
                        # Calculate timestamp within the video
                        frame_timestamp = frame_nmr / fps if fps > 0 else 0
                        hours, remainder = divmod(frame_timestamp, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        timecode = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                        
                        # Calculate absolute timestamp based on current time
                        detection_time = datetime.now()
                        
                        # Check if this is a stolen vehicle
                        stolen_vehicle = None
                        if HAVE_DB_UTILS:
                            try:
                                # Try with database_utils
                                stolen_vehicle = check_license_plate_in_database(license_plate_text)
                            except Exception as e:
                                # Fallback to direct check if context error
                                print(f"Database context error, using fallback: {e}")
                                stolen_vehicle = fallback_check_license_plate(license_plate_text)
                        
                        if stolen_vehicle:
                            # Skip if we've already detected this license plate in this video
                            if license_plate_text in detected_license_plates:
                                continue
                            
                            # Add to set of detected plates
                            detected_license_plates.add(license_plate_text)
                            
                            # Print alert only if alert_on_match is True
                            if alert_on_match:
                                print(f"⚠️ STOLEN VEHICLE DETECTED ⚠️")
                                print(f"Frame #{frame_nmr}, Vehicle #{car_id}, Timecode: {timecode}")
                                print(f"License: {license_plate_text} (Confidence: {license_plate_text_score:.2f})")
                                print(f"Vehicle Info: {stolen_vehicle.get('year', 'N/A')} " +
                                     f"{stolen_vehicle.get('make', 'N/A')} " +
                                     f"{stolen_vehicle.get('model', 'N/A')} " +
                                     f"({stolen_vehicle.get('color', 'N/A')})")
                                print(f"Description: {stolen_vehicle.get('description', 'N/A')}")
                                print("-" * 50)
                            
                            # Save the frame
                            frame_filename = None
                            if save_frames:
                                timestamp_str = detection_time.strftime("%Y%m%d_%H%M%S")
                                frame_filename = f"{frames_output_dir}/stolen_{license_plate_text}_frame_{frame_nmr}_{timestamp_str}.jpg"
                                
                                # Draw bounding boxes on the frame
                                frame_copy = frame.copy()
                                # Draw car bbox in red
                                cv2.rectangle(frame_copy, 
                                            (int(xcar1), int(ycar1)), 
                                            (int(xcar2), int(ycar2)), 
                                            (0, 0, 255), 3)
                                # Draw license plate bbox in yellow
                                cv2.rectangle(frame_copy, 
                                            (int(x1), int(y1)), 
                                            (int(x2), int(y2)), 
                                            (0, 255, 255), 2)
                                # Add text
                                cv2.putText(frame_copy, 
                                          f"STOLEN: {license_plate_text}", 
                                          (int(xcar1), int(ycar1) - 10), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.9, 
                                          (0, 0, 255), 2)
                                
                                # Save the annotated frame
                                cv2.imwrite(frame_filename, frame_copy)
                            
                            # Record the detection event in the database
                            if HAVE_DB_UTILS:
                                try:
                                    detection_id = record_detection_event(
                                        license_plate=license_plate_text,
                                        vehicle_id=stolen_vehicle.get('id'),
                                        frame_number=frame_nmr,
                                        timestamp=detection_time,
                                        confidence=license_plate_text_score,
                                        video_path=video_path,
                                        image_path=frame_filename if save_frames else None,
                                        job_id=job_id,
                                        user_id=user_id
                                    )
                                except Exception as e:
                                    # Fallback to direct recording if context error
                                    print(f"Database context error in recording, using fallback: {e}")
                                    detection_id = fallback_record_detection(
                                        license_plate=license_plate_text,
                                        vehicle_id=stolen_vehicle.get('id'),
                                        frame_number=frame_nmr,
                                        timestamp=detection_time.strftime('%Y-%m-%d %H:%M:%S'),
                                        confidence=license_plate_text_score,
                                        video_path=video_path,
                                        image_path=frame_filename
                                    )
                            
                            # Add to detection results
                            detection_results.append({
                                'license_plate': license_plate_text,
                                'confidence': license_plate_text_score,
                                'frame': frame_nmr,
                                'timecode': timecode,
                                'timestamp': detection_time,
                                'vehicle': stolen_vehicle,
                                'image_path': frame_filename
                            })
    
    # Release video capture
    cap.release()
    
    # write results to CSV if requested
    if save_detections:
        write_csv(results, output_path)
    
    return detection_results

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ANPR Stolen Vehicle Detection')
    parser.add_argument('--video', type=str, default='./sample2.mp4', help='Path to input video file')
    parser.add_argument('--output', type=str, default='./test.csv', help='Path to output CSV file')
    parser.add_argument('--show-alerts', action='store_true', help='Show console alerts for stolen vehicles (default: hidden)')
    parser.add_argument('--no-frames', action='store_true', help='Disable saving frames of stolen vehicles')
    args = parser.parse_args()
    
    # Process the video
    detection_results = process_video(
        video_path=args.video,
        output_path=args.output,
        alert_on_match=args.show_alerts,
        save_frames=not args.no_frames
    )
    
    # Print summary
    print(f"\nVideo processing complete: {args.video}")
    
    if detection_results:
        # Only show the summary line if alerts are disabled (to avoid duplicate output)
        if not args.show_alerts:
            print(f"\nDetected {len(detection_results)} stolen vehicles (see visualization for details)")
    else:
        print("\nNo stolen vehicles detected in this video.")