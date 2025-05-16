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
            annotate_video(filepath, out_filepath, model)
            logging.info(f"Video processing complete: {out_filepath}")

            # For videos, show the annotated video file
            return render_template('result.html', annotated_video=out_filename, is_video=True)

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