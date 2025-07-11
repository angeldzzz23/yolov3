import base64
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request

from utils.downloads import safe_download

app = Flask(__name__)

@app.route("/update-model/<model_name>", methods=["POST"])
def update_model(model_name):
    if not model_name:
        return jsonify({"error": "Model name is required"}), 400
    
    # Download the specified model
    model_file = Path(f"{model_name}.pt")
    safe_download(
        file=model_file,
        url=f"https://storage.googleapis.com/nsh25-yolov3-weights/{model_name}.pt",
        min_bytes=1e5,
        error_msg=f"{model_name}.pt could not be downloaded"
    )

    return jsonify({"message": f"Model {model_name} download complete"}), 200

@app.route("/detect", methods=["POST"])
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image = request.files["image"]
    image_path = "/tmp/image.jpg"
    image.save(image_path)

    cmd = ["rm", "-rf", "runs/detect"]
    subprocess.run(cmd, capture_output=True, text=True)
    
    # Run YOLOv3 detection
    cmd = ["python", "detect.py", "--weights", "yolov5l.pt", "--img", "640", "--conf", "0.25", "--source", image_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Get the output image
    output_image_path = "runs/detect/exp/image.jpg"
    with open(output_image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
    
    return jsonify({
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.returncode,
        "image": encoded_image
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
