import os
import uuid
import logging
import traceback
from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
import cv2  # For saving annotated images

# ------------------ Setup ------------------

# Initialize logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------ Load YOLO Model ------------------

# Try loading the ONNX model first for better performance on CPU
try:
    model = YOLO('best.onnx')  # Make sure 'best.onnx' is in the project root
    logging.info("Loaded ONNX model (best.onnx)")
except Exception as e:
    logging.warning("Failed to load ONNX model. Falling back to PyTorch model (best.pt).")
    logging.warning(traceback.format_exc())
    model = YOLO('best.pt')  # Fallback to PyTorch if ONNX loading fails

# ------------------ Routes ------------------

@app.route('/')
def index():
    """Home page with upload form."""
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Handles image upload and runs object detection."""
    if request.method == 'GET':
        return redirect(url_for('index'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        try:
            # Save uploaded image with a unique filename
            filename = f"{uuid.uuid4()}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Run YOLO prediction on the image
            results = model(filepath)

            # Save annotated image (with bounding boxes) over the original file
            annotated_img = results[0].plot()
            cv2.imwrite(filepath, annotated_img)

            # Extract object class names from results
            labels_dict = results[0].names
            boxes = results[0].boxes
            detected_objects = []
            for box in boxes:
                class_id = int(box.cls[0])
                label = labels_dict[class_id]
                detected_objects.append(label)

            # Render the result template showing the image and labels
            return render_template('result.html', user_image=filename, detected_objects=detected_objects)

        except Exception as e:
            # Log error for debugging
            logging.error("Error during prediction: %s", e)
            logging.error(traceback.format_exc())
            return "Internal Server Error during prediction. Check server logs for details.", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files from the static directory."""
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

# ------------------ Run Server ------------------

if __name__ == '__main__':
    # Run the app on all interfaces (host 0.0.0.0), port 8080
    app.run(host="0.0.0.0", port=8080, debug=True)
