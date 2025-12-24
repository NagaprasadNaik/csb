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

from datetime import datetime
from flask import request, jsonify
import os

@app.route("/home", methods=["POST"])
def home_reset():
    data = request.json or {}

    # ---------------- SAVE LOGS ----------------
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save Evenness CSV
    if data.get("evenness", "").strip():
        with open(f"logs/evenness_{timestamp}.csv", "w") as f:
            f.write(data["evenness"])

    # Save Neatness & Cleanness CSV
    if data.get("neatness", "").strip():
        with open(f"logs/neatness_cleanness_{timestamp}.csv", "w") as f:
            f.write(data["neatness"])

    # ---------------- DELETE RESULT CSVs ----------------
    for fpath in [
        os.path.join(RESULT_DIR, "evenness.csv"),
        os.path.join(RESULT_DIR, "neatness_cleanness.csv")
    ]:
        if os.path.exists(fpath):
            os.remove(fpath)

    # ---------------- DELETE PREPROCESSED IMAGES ----------------
    PREPROCESSED_DIR = os.path.join(BASE_DIR, "preprocessed")

    if os.path.exists(PREPROCESSED_DIR):
        for filename in os.listdir(PREPROCESSED_DIR):
            file_path = os.path.join(PREPROCESSED_DIR, filename)

            # delete only files (images)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # ---------------- DELETE EVENNESS IMAGES ----------------
    # PREPROCESSED_DIR = os.path.join(BASE_DIR, "results/evenness")

    # if os.path.exists(PREPROCESSED_DIR):
    #     for filename in os.listdir(PREPROCESSED_DIR):
    #         file_path = os.path.join(PREPROCESSED_DIR, filename)

    #         # delete only files (images)
    #         if os.path.isfile(file_path):
    #             os.remove(file_path)

# ---------------- DELETE NEATNESS IMAGES ----------------
    # PREPROCESSED_DIR = os.path.join(BASE_DIR, "results/neatness")

    # if os.path.exists(PREPROCESSED_DIR):
    #     for filename in os.listdir(PREPROCESSED_DIR):
    #         file_path = os.path.join(PREPROCESSED_DIR, filename)

    #         # delete only files (images)
    #         if os.path.isfile(file_path):
    #             os.remove(file_path)

    return jsonify({"status": "saved_all_and_reset"})


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
