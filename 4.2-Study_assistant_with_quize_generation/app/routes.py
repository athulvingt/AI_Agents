from flask import Blueprint, render_template, request, current_app, jsonify
from werkzeug.utils import secure_filename
from backend import extract_text_from_pdf
from backend import generate_summary_quiz
import os

main = Blueprint("main", __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route("/extract-text", methods=["POST"])
def extract_text():
    file = request.files.get("pdf_file")
    if not file:
        return {"error": "No file uploaded"}, 400
    text = extract_text_from_pdf(file)
    return {"text": text}, 200

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@main.route("/generate-summary", methods=["POST"])
def generate_summary():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    study_text = data['text']
    result = generate_summary_quiz(study_text)
    return jsonify(result), 200