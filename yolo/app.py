import os
import cv2
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from ultralytics import YOLO
from collections import defaultdict
from datetime import datetime
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
CORS(app) 
# Load YOLOv8 model
MODEL_PATH = "bestt.pt"
model = YOLO(MODEL_PATH)

# Ensure output directory exists
OUTPUT_DIR = "static/output"
INPUT_DIR = "static/input"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# Log file
LOG_FILE = "logs.xlsx"

# Class categories
CLEANLINESS_CLASSES = {"minor", "major", "supermajor"}
NEATNESS_CLASSES = {"neatness"}


def log_to_excel(timestamp, image_name, cleanliness, neatness, total):
    # Flatten counts into one dict
    log_entry = {
        "Timestamp": timestamp,
        "Image Name": image_name,
        **{f"Cleanliness - {k}": cleanliness.get(k, 0) for k in CLEANLINESS_CLASSES},
        **{f"Neatness - {k}": neatness.get(k, 0) for k in NEATNESS_CLASSES},
        "Total Defects": total
    }

    # Append or create Excel
    df_new = pd.DataFrame([log_entry])

    if os.path.exists(LOG_FILE):
        df_existing = pd.read_excel(LOG_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(LOG_FILE, index=False)


# @app.route('/')
# def home():
#     return jsonify({"message": "YOLOv8 Inference API is running!"})

@app.route("/")
def index():
    return render_template("index.html") 

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # filename = os.path.basename(file.filename)
        filename = "result.jpg" 

        # Run inference
        results = model(img)
        annotated_img = results[0].plot()

        # Save annotated image
        input_filename = "input.jpg"
        input_path = os.path.join(INPUT_DIR, input_filename)
        cv2.imwrite(input_path, img)

        output_path = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(output_path, annotated_img)

        # Count defects
        defect_counts = defaultdict(int)
        total_defects = 0
        if results[0].boxes:
            names = results[0].names
            for cls_id in results[0].boxes.cls.cpu().numpy():
                cls_name = names[int(cls_id)]
                defect_counts[cls_name] += 1
                total_defects += 1

        # Organize counts
        cleanliness = {cls: defect_counts.get(cls, 0) for cls in CLEANLINESS_CLASSES}
        neatness = {cls: defect_counts.get(cls, 0) for cls in NEATNESS_CLASSES}

        # Log to Excel
        log_to_excel(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), filename, cleanliness, neatness, total_defects)

        # JSON response
        response = {
            "Cleanliness": cleanliness,
            "Neatness": neatness,
            "Total": total_defects,
            "output_image": output_path
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)
