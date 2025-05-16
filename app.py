import os
import uuid
import logging
import traceback
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from ultralytics import YOLO
import cv2
from videocapture import annotate_video

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DEBUG_FOLDER'] = 'static/uploads/debug_frames'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DEBUG_FOLDER'], exist_ok=True)

# Load your ONNX or PyTorch model
model = YOLO('best.onnx')  # or 'best.pt' if you want to use the PyTorch model

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return redirect(url_for('index'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    try:
        # Generate unique filename and save the uploaded file
        ext = os.path.splitext(file.filename)[1].lower()
        allowed_image_exts = {'.jpg', '.jpeg', '.png'}
        allowed_video_exts = {'.mp4', '.avi', '.mov', '.mkv'}

        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if ext in allowed_image_exts:
            # --- IMAGE PROCESSING ---
            results = model(filepath)
            annotated_img = results[0].plot()
            cv2.imwrite(filepath, annotated_img)

            # Extract detected objects
            labels_dict = results[0].names
            boxes = results[0].boxes
            detected_objects = []
            for box in boxes:
                class_id = int(box.cls[0])
                detected_objects.append(labels_dict[class_id])

            return render_template('result.html', user_image=filename, detected_objects=detected_objects, is_video=False)

        elif ext in allowed_video_exts:
            # --- VIDEO PROCESSING ---
            # Generate output filename
            out_filename = f"{uuid.uuid4()}_annotated.mp4"
            out_filepath = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
            
            # Use the dedicated video processing function
            logging.info(f"Processing video: {filepath}")
            try:
                frame_count, total_detections = annotate_video(filepath, out_filepath, model)
                logging.info(f"Video processing complete: {out_filepath} - {frame_count} frames with {total_detections} detections")
                
                # Get some debug frames for preview
                debug_frames = []
                debug_dir = app.config['DEBUG_FOLDER']
                debug_files = os.listdir(debug_dir)
                
                # Sort and get 5 evenly spaced frames for preview
                if debug_files:
                    debug_files.sort()
                    if len(debug_files) > 5:
                        step = len(debug_files) // 5
                        preview_files = [debug_files[i*step] for i in range(5)]
                    else:
                        preview_files = debug_files
                    
                    for file in preview_files:
                        if file.startswith("frame_") and file.endswith(".jpg"):
                            debug_frames.append(file)
                
                # For videos, show the annotated video file
                return render_template('result.html', 
                                      annotated_video=out_filename, 
                                      is_video=True, 
                                      debug_frames=debug_frames,
                                      frame_count=frame_count,
                                      detection_count=total_detections)
            except Exception as e:
                logging.error(f"Error in video processing: {str(e)}")
                return f"Error processing video: {str(e)}", 500

        else:
            return "Unsupported file type.", 400

    except Exception as e:
        logging.error("Error during prediction: %s", e)
        logging.error(traceback.format_exc())
        return "Internal Server Error during prediction. Check server logs for details.", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve uploaded and processed files from upload folder
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/debug_frames/<filename>')
def debug_frame(filename):
    # Serve debug frames
    return send_from_directory(app.config['DEBUG_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)