from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from models.detects import detect_deepfake

app = Flask(__name__)

# Folder to temporarily store uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    if 'media' not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    video = request.files['media']
    if video.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(video.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    video.save(filepath)

    try:
        # Analyze video
        result = detect_deepfake(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
