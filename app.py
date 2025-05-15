import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLOv8 model (ensure 'best.pt' is in the project directory or provide full path)
model = YOLO('best.pt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        # Redirect GET requests to the home page
        return redirect(url_for('index'))

    # Handle POST (file upload)
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Save the uploaded image
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run YOLOv8 detection
        results = model(filepath)
        results[0].save(filename=filepath)  # Save annotated image in-place

        # Extract labels from detections
        labels_dict = results[0].names
        boxes = results[0].boxes
        detected_objects = []

        for box in boxes:
            class_id = int(box.cls[0])
            label = labels_dict[class_id]
            detected_objects.append(label)

        return render_template('result.html', user_image=filename, detected_objects=detected_objects)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Redirect to static file URL
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    # For Docker compatibility
    app.run(host='0.0.0.0', port=8080)
