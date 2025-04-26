import base64
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

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

    print(result.stdout)
    print(result.stderr)

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
    app.run(host="0.0.0.0", port=5000)
