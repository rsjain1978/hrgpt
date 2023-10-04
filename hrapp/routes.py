from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from .models import Candidate
from .utils import allowed_file, load_pdf, parse_and_analyze_resume, analyze_resume

bp = Blueprint('routes', __name__)

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/upload", methods=["POST"])
def upload_resumes():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    job_description = request.form.get('job_description', '')

    if file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(bp.root_path, '..', 'uploads', filename))

        resume = load_pdf(filename)
        resume_metadata = parse_and_analyze_resume(resume)  # Adjust with the parsing logic
        analysis_result = analyze_resume(resume_metadata, job_description)  # Adjust with the analysis logic

        return jsonify(success=True, message=analysis_result), 200

    return jsonify({"error": "Invalid file type"}), 400
