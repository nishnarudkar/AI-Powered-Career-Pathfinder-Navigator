# development/app.py

from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
import PyPDF2
from docx import Document
from dotenv import load_dotenv
from werkzeug.utils import secure_filename  # Import secure_filename
from career_pathfinder_langgraph import run_pipeline
from career_logger import CareerPathfinderLogger
import time
import traceback

app = Flask(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not OPENAI_API_KEY or not LANGSMITH_API_KEY:
    raise ValueError("OPENAI_API_KEY and LANGSMITH_API_KEY must be set in .env file")

# Initialize logger
logger = CareerPathfinderLogger()

# --- START: Recommended Changes for Robust Paths ---
# Create absolute paths based on the location of this file (app.py)
APP_ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = APP_ROOT / "uploads"
DATA_DIR = APP_ROOT / "data"

# Ensure directories exist using pathlib
UPLOADS_DIR.mkdir(exist_ok=True)
# --- END: Recommended Changes ---

# Check for data files
JOB_ROLES_PATH = DATA_DIR / "job_roles.json"
COURSES_PATH = DATA_DIR / "courses.json"

if not JOB_ROLES_PATH.exists() or not COURSES_PATH.exists():
    print(f"⚠️ Curated data files not found at {JOB_ROLES_PATH} or {COURSES_PATH}, using AI-only mode")

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    # --- START: Added Full Try/Except Block for Error Handling ---
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file part in the request'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Validate file type
        if file and file.filename.lower().endswith(('.pdf', '.docx')):
            # Secure the filename to prevent malicious paths
            filename = secure_filename(file.filename)
            file_path = UPLOADS_DIR / filename
            file.save(file_path)

            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_path)
            else:
                resume_text = extract_text_from_docx(file_path)

            if not resume_text.strip():
                return jsonify({'success': False, 'error': 'Could not extract text from the resume'}), 500

            # Store resume text in a session file
            session_id = f"session_{int(time.time())}"
            session_file = UPLOADS_DIR / f"{session_id}.txt"
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(resume_text)

            return jsonify({'success': True, 'session_id': session_id})
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type. Please upload a PDF or DOCX.'}), 400

    except Exception as e:
        # Log the full error to the console for debugging
        print(f"An error occurred during resume upload: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'A server-side error occurred during file processing.'}), 500
    # --- END: Added Full Try/Except Block ---


@app.route('/extract-skills', methods=['POST'])
def extract_skills():
    session_id = request.json.get('session_id') if request.is_json else None
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400

    session_file = UPLOADS_DIR / f"{session_id}.txt"
    if not session_file.exists():
        return jsonify({'success': False, 'error': 'Session file not found'}), 404

    with open(session_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    try:
        start_time = time.time()
        result = run_pipeline(resume_text, "Unknown Role", log_execution=False)
        execution_time = time.time() - start_time
        logger.log_execution(resume_text, "Unknown Role", result, execution_time)
        return jsonify({'success': True, 'skills': result.get('extracted_skills', [])})
    except Exception as e:
        print(f"Skill extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    skills = data.get('skills', [])
    role = data.get('role', '')
    session_id = data.get('session_id', '')

    if not role:
        return jsonify({'success': False, 'error': 'No role selected'}), 400
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400

    session_file = UPLOADS_DIR / f"{session_id}.txt"
    if not session_file.exists():
        return jsonify({'success': False, 'error': 'Session file not found'}), 404

    with open(session_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    try:
        start_time = time.time()
        result = run_pipeline(resume_text, role, log_execution=True)
        
        # Format roadmap for frontend
        roadmap = []
        if result.get('roadmap'):
            for phase in result.get('roadmap', []):
                phase_data = {
                    'phase': phase.get('phase', 'Unknown Phase'),
                    'skills': []
                }
                for item in phase.get('skills', phase.get('items', [])):
                    course_info = item.get('course', {})
                    if isinstance(course_info, dict):
                        phase_data['skills'].append({
                            'skill': item.get('skill', ''),
                            'course': {
                                'title': course_info.get('title', 'N/A'),
                                'platform': course_info.get('platform', 'N/A'),
                                'url': course_info.get('url', '#'),
                                'reason': course_info.get('why', item.get('reason', 'N/A'))
                            }
                        })
                roadmap.append(phase_data)

        response = {
            'success': True,
            'roadmap': roadmap,
        }
        return jsonify(response)
    except Exception as e:
        print(f"Roadmap generation error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)