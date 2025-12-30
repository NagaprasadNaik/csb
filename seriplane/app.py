from flask import Flask, jsonify, send_file
import subprocess
import os
from datetime import datetime
from flask import request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(BASE_DIR, "results")

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return app.send_static_file("index.html")


import shutil
import re

@app.route("/home", methods=["POST"])
def home_reset():
    data = request.json or {}

    # ---------------- BASE DIRECTORIES ----------------
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    RESULT_DIR = os.path.join(BASE_DIR, "results")
    PREPROCESSED_DIR = os.path.join(BASE_DIR, "preprocessed")

    os.makedirs(LOGS_DIR, exist_ok=True)

    # ---------------- FIND NEXT PANEL NUMBER ----------------
    panel_numbers = []

    for name in os.listdir(LOGS_DIR):
        match = re.match(r"panel(\d+)", name)
        if match:
            panel_numbers.append(int(match.group(1)))

    next_panel = max(panel_numbers) + 1 if panel_numbers else 1

    if next_panel > 100:
        return jsonify({"error": "Maximum panel limit reached"}), 400

    PANEL_DIR = os.path.join(LOGS_DIR, f"panel{next_panel}")
    os.makedirs(PANEL_DIR)

    # ---------------- SAVE UPDATED CSVs ----------------
    if data.get("evenness", "").strip():
        with open(os.path.join(PANEL_DIR, "evenness.csv"), "w") as f:
            f.write(data["evenness"])

    if data.get("neatness", "").strip():
        with open(os.path.join(PANEL_DIR, "neatness_cleanness.csv"), "w") as f:
            f.write(data["neatness"])

    # ---------------- COPY RESULT SUBFOLDERS ----------------
    for sub in ["evenness", "neatness"]:
        src = os.path.join(RESULT_DIR, sub)
        dst = os.path.join(PANEL_DIR, sub)

        if os.path.exists(src):
            shutil.copytree(src, dst)

    # ---------------- CLEAN RESULT CSVs ----------------
    for f in ["evenness.csv", "neatness_cleanness.csv"]:
        path = os.path.join(RESULT_DIR, f)
        if os.path.exists(path):
            os.remove(path)

    # ---------------- CLEAN PREPROCESSED IMAGES ----------------
    if os.path.exists(PREPROCESSED_DIR):
        for file in os.listdir(PREPROCESSED_DIR):
            file_path = os.path.join(PREPROCESSED_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # ---------------- DELETE EVENNESS IMAGES ----------------
    EVENNESS_DIR = os.path.join(BASE_DIR, "results/evenness")

    if os.path.exists(EVENNESS_DIR):
        for filename in os.listdir(EVENNESS_DIR):
            file_path = os.path.join(EVENNESS_DIR, filename)

            # delete only files (images)
            if os.path.isfile(file_path):
                os.remove(file_path)

# ---------------- DELETE NEATNESS IMAGES ----------------
    NEATNESS_DIR = os.path.join(BASE_DIR, "results/neatness")

    if os.path.exists(NEATNESS_DIR):
        for filename in os.listdir(NEATNESS_DIR):
            file_path = os.path.join(NEATNESS_DIR, filename)

            # delete only files (images)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return jsonify({
        "status": "panel_saved",
        "panel": f"panel{next_panel}"
    })


@app.route("/execute", methods=["POST"])
def execute_pipeline():
    subprocess.run(["python", "pipeline.py"], check=True)
    return jsonify({"status": "Pipeline executed"})

@app.route("/csv/<name>")
def get_csv(name):
    if name == "evenness":
        file_path = os.path.join(RESULT_DIR, "evenness.csv")
    elif name == "neatness":
        file_path = os.path.join(RESULT_DIR, "neatness_cleanness.csv")
    else:
        return "Invalid CSV", 404

    if not os.path.exists(file_path):
        return "", 204   # No Content (important)

    return send_file(file_path, mimetype="text/csv")


if __name__ == "__main__":
    app.run(debug=True)
