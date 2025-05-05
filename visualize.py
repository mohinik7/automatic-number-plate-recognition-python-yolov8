import ast

import cv2
import numpy as np
import pandas as pd
import argparse
import os

# Import database utilities for stolen vehicle checking
try:
    from database_utils import check_license_plate_in_database
    HAVE_DB_UTILS = True
except ImportError:
    print("Warning: database_utils not available, running without stolen vehicle checks")
    HAVE_DB_UTILS = False


def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)  #-- top-left
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)  #-- bottom-left
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)  #-- top-right
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)  #-- bottom-right
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


def visualize(input_csv='./output/test_interpolated.csv', video_path='sample2.mp4', output_path='./out.mp4', 
              display_preview=False, save_video=True, check_stolen=True):
    """
    Visualize license plate detection results
    
    Args:
        input_csv (str): Path to the interpolated CSV file
        video_path (str): Path to the original video file
        output_path (str): Path to save the output video
        display_preview (bool): Whether to display a preview window
        save_video (bool): Whether to save the output video
        check_stolen (bool): Whether to check for stolen vehicles
    """
    results = pd.read_csv(input_csv)

    # load video
    cap = cv2.VideoCapture(video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the codec
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Only create VideoWriter if saving is enabled
    out = None
    if save_video:
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Create dictionary to track stolen vehicles
    stolen_vehicles = {}
    detected_plates = set()
    
    # Process license plates for each car
    license_plate = {}
    for car_id in np.unique(results['car_id']):
        max_ = np.amax(results[results['car_id'] == car_id]['license_number_score'])
        license_text = results[(results['car_id'] == car_id) & 
                              (results['license_number_score'] == max_)]['license_number'].iloc[0]
        
        license_plate[car_id] = {
            'license_crop': None,
            'license_plate_number': license_text
        }
        
        # Check if this is a stolen vehicle
        if HAVE_DB_UTILS and check_stolen and license_text != '0':
            vehicle_info = check_license_plate_in_database(license_text)
            if vehicle_info:
                stolen_vehicles[car_id] = vehicle_info
        
        # Get the license plate crop
        cap.set(cv2.CAP_PROP_POS_FRAMES, results[(results['car_id'] == car_id) &
                                               (results['license_number_score'] == max_)]['frame_nmr'].iloc[0])
        ret, frame = cap.read()

        x1, y1, x2, y2 = ast.literal_eval(results[(results['car_id'] == car_id) &
                                               (results['license_number_score'] == max_)]['license_plate_bbox'].iloc[0].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))

        license_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
        # Reduce the size of the license plate image to 200px height (half of original)
        license_crop = cv2.resize(license_crop, (int((x2 - x1) * 200 / (y2 - y1)), 200))

        license_plate[car_id]['license_crop'] = license_crop


    frame_nmr = -1

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # read frames
    ret = True
    while ret:
        ret, frame = cap.read()
        frame_nmr += 1
        if ret:
            df_ = results[results['frame_nmr'] == frame_nmr]
            for row_indx in range(len(df_)):
                car_id = int(float(df_.iloc[row_indx]['car_id']))
                
                # Check if this car is a stolen vehicle
                is_stolen = car_id in stolen_vehicles
                
                # Set colors based on whether the vehicle is stolen
                border_color = (0, 0, 255) if is_stolen else (0, 255, 0)  # Red for stolen, Green for normal
                rect_color = (0, 0, 255) if is_stolen else (0, 0, 255)    # Red for stolen plate, Blue for normal
                
                # draw car boundary (use original thickness parameters)
                car_x1, car_y1, car_x2, car_y2 = ast.literal_eval(df_.iloc[row_indx]['car_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                draw_border(frame, (int(car_x1), int(car_y1)), (int(car_x2), int(car_y2)), border_color, 10,
                            line_length_x=200, line_length_y=200)

                # draw license plate (use original thickness)
                x1, y1, x2, y2 = ast.literal_eval(df_.iloc[row_indx]['license_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), rect_color, 12)

                # Print alerts for stolen vehicles (only once per vehicle per visualization)
                license_text = license_plate[car_id]['license_plate_number']
                if is_stolen and license_text not in detected_plates and license_text != '0':
                    detected_plates.add(license_text)
                    vehicle_info = stolen_vehicles[car_id]
                    
                    # Calculate timestamp within the video
                    frame_timestamp = frame_nmr / fps if fps > 0 else 0
                    hours, remainder = divmod(frame_timestamp, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    timecode = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                    
                    # Print alert
                    print(f"\n⚠️ STOLEN VEHICLE DETECTED ⚠️")
                    print(f"Frame #{frame_nmr}, Vehicle #{car_id}, Timecode: {timecode}")
                    print(f"License: {license_text}")
                    print(f"Vehicle Info: {vehicle_info.get('year', 'N/A')} " +
                          f"{vehicle_info.get('make', 'N/A')} " +
                          f"{vehicle_info.get('model', 'N/A')} " +
                          f"({vehicle_info.get('color', 'N/A')})")
                    print(f"Description: {vehicle_info.get('description', 'N/A')}")
                    print("-" * 50)

                # crop license plate
                license_crop = license_plate[car_id]['license_crop']

                H, W, _ = license_crop.shape

                try:
                    # Calculate vertical position to avoid overlap - reduced padding
                    vertical_padding = 50
                    # Place license plate image above car with reduced spacing
                    frame[int(car_y1) - H - vertical_padding:int(car_y1) - vertical_padding,
                          int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = license_crop

                    # Background color for license text - light red for stolen, white for normal
                    bg_color = (220, 220, 255) if is_stolen else (255, 255, 255)
                    # Place text background with reduced height (130px instead of 300px)
                    bg_height = 130
                    frame[int(car_y1) - H - vertical_padding - bg_height:int(car_y1) - H - vertical_padding,
                          int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = bg_color

                    # Reduce text size
                    font_scale = 2.0  # Reduced from 4.3
                    thickness = 6     # Reduced from 17
                    (text_width, text_height), _ = cv2.getTextSize(
                        license_plate[car_id]['license_plate_number'],
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale,
                        thickness)

                    # Text color - black for all text
                    text_color = (0, 0, 0)
                    # Adjust text position to center it in the background
                    text_y_position = int(car_y1) - H - vertical_padding - bg_height//2 + text_height//2
                    cv2.putText(frame,
                                license_plate[car_id]['license_plate_number'],
                                (int((car_x2 + car_x1 - text_width) / 2), text_y_position),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale,
                                text_color,
                                thickness)

                    # Add "STOLEN" label for stolen vehicles (with small font size)
                    if is_stolen:
                        cv2.putText(frame,
                                    "STOLEN",
                                    (int(car_x1), int(car_y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.0,  # Smaller font size
                                    (0, 0, 255),  # Red
                                    2)  # Thinner text

                except:
                    pass

            if save_video:
                out.write(frame)
            
            if display_preview:
                # Resize for display to fit on most screens
                display_frame = cv2.resize(frame, (1280, 720))
                cv2.imshow('License Plate Detection', display_frame)
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    if save_video:
        out.release()
    cap.release()
    
    # Close all OpenCV windows if preview was enabled
    if display_preview:
        cv2.destroyAllWindows()
        
    print(f"Processing complete.")
    if save_video:
        print(f"Output video saved to: {output_path}")
    
    # Print summary of stolen vehicles
    if len(stolen_vehicles) > 0:
        print(f"\nTotal stolen vehicles detected: {len(stolen_vehicles)}")
        for car_id, vehicle in stolen_vehicles.items():
            print(f"  - {vehicle.get('license_plate')}: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
    else:
        print("\nNo stolen vehicles detected in this video.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize license plate detection results')
    parser.add_argument('--input-csv', type=str, default='./output/test_interpolated.csv', help='Path to interpolated CSV file')
    parser.add_argument('--video', type=str, default='sample2.mp4', help='Path to original video file')
    parser.add_argument('--output', type=str, default='./out.mp4', help='Path to save output video')
    parser.add_argument('--preview', action='store_true', help='Display preview window')
    parser.add_argument('--no-save', action='store_true', help='Disable saving output video')
    parser.add_argument('--no-stolen-check', action='store_true', help='Disable stolen vehicle checking')
    args = parser.parse_args()
    
    visualize(
        input_csv=args.input_csv,
        video_path=args.video,
        output_path=args.output,
        display_preview=args.preview,
        save_video=not args.no_save,
        check_stolen=not args.no_stolen_check
    )
