import io
from flask import Blueprint, request, jsonify, render_template, current_app
from PIL import Image

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def index():
    """Render the home page with a drag‑and‑drop upload box."""
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    """Accept an image, run detection, and return JSON results."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        image = Image.open(file.stream).convert('RGB')
    except Exception as e:
        return jsonify({'error': f'Invalid image: {str(e)}'}), 400

    detector = current_app.detector
    results = detector.predict(image)
    return jsonify({'detections': results})
