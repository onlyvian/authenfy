from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from detect import detect_deepfake  # This should be your updated detect function

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Set the upload folder for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Upload page route
@app.route('/upload')
def upload():
    return render_template('upload.html')

# Analyze page route
@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

# Contact page route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Form page route
@app.route('/form')
def form():
    return render_template('form.html')

# Deepfake detection API endpoint
@app.route('/detect', methods=['POST'])
def detect():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(video.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(filepath)

    try:
        result = detect_deepfake(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Remove the video file after processing
        if os.path.exists(filepath):
            os.remove(filepath)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
