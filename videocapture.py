import cv2
from ultralytics import YOLO
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def annotate_video(input_path, output_path, model):
    """
    Process a video file with the YOLOv8 model and save an annotated version.
    
    Args:
        input_path: Path to the input video file
        output_path: Path to save the annotated video
        model: Loaded YOLO model
    """
    logger.info(f"Starting video annotation: {input_path} -> {output_path}")
    
    # Open the video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video file: {input_path}")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Handle invalid FPS
    if fps is None or fps <= 0 or fps != fps:  # NaN check
        logger.warning("Invalid FPS detected, using default value of 30")
        fps = 30
    
    logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
    
    # Set up video writer with proper codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Make debug directory
    debug_dir = "static/uploads/debug_frames"
    os.makedirs(debug_dir, exist_ok=True)
    
    frame_count = 0
    total_detections = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame with YOLO
            results = model(frame, conf=0.1)  # Lower confidence threshold for more detections
            detected_objects = len(results[0].boxes)
            total_detections += detected_objects
            
            # Log progress periodically
            if frame_count % 10 == 0 or frame_count < 5:
                logger.info(f"Frame {frame_count}/{total_frames}: detected {detected_objects} objects")
            
            # Get the annotated frame
            annotated_frame = results[0].plot()
            
            # Save debug frame (save all frames, not just first 5)
            debug_path = os.path.join(debug_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(debug_path, annotated_frame)
            
            # Write to output video
            out.write(annotated_frame)
            frame_count += 1
    
    except Exception as e:
        logger.error(f"Error during video processing: {str(e)}")
        raise
    
    finally:
        # Clean up resources
        cap.release()
        out.release()
        
    logger.info(f"Video annotation complete. Processed {frame_count} frames with {total_detections} total detections")
    return frame_count, total_detections