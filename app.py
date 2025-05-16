import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
import cv2  # for saving annotated images

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLOv8 model (make sure 'best.pt' is in your project directory or update the path)
model = YOLO('best.pt')

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

    if file:
        # Generate unique filename and save the uploaded file
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run YOLOv8 prediction
        results = model(filepath)

        # Get annotated image as numpy array and save it to the same filepath
        annotated_img = results[0].plot()
        cv2.imwrite(filepath, annotated_img)

        # Extract detected object labels
        labels_dict = results[0].names
        boxes = results[0].boxes
        detected_objects = []
        for box in boxes:
            class_id = int(box.cls[0])
            label = labels_dict[class_id]
            detected_objects.append(label)

        # Render result page with image and detected objects
        return render_template('result.html', user_image=filename, detected_objects=detected_objects)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Redirect to static file URL for uploaded images
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    # Run app on all interfaces, port 8080 (common for deployment)
    app.run(host="0.0.0.0", port=8080, debug=True)
