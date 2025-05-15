import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load your YOLOv8 model
model = YOLO('best.pt')  # Replace with your model filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        # Redirect GET requests on /predict back to homepage to avoid errors
        return redirect(url_for('index'))

    # POST method handling
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Generate unique filename and save upload
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run detection
        results = model(filepath)

        # Save annotated image (this overwrites original upload with detection boxes)
        results[0].save(filename=filepath)

        # Extract detected object labels
        labels_dict = results[0].names
        boxes = results[0].boxes
        detected_objects = []
        for box in boxes:
            class_id = int(box.cls[0])
            label = labels_dict[class_id]
            detected_objects.append(label)

        # Render result template with image and detected objects
        return render_template('result.html', user_image=filename, detected_objects=detected_objects)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve uploaded files
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == '__main__':
    app.run(debug=True)
