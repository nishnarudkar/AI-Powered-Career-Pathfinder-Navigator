from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
import PyPDF2
from docx import Document
from dotenv import load_dotenv
from career_pathfinder_langgraph import run_pipeline
from career_logger import CareerPathfinderLogger
import time

app = Flask(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not OPENAI_API_KEY or not LANGSMITH_API_KEY:
    raise ValueError("OPENAI_API_KEY and LANGSMITH_API_KEY must be set in .env file")

# Initialize logger
logger = CareerPathfinderLogger()

# Ensure uploads directory exists
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Check for data files
DATA_DIR = "data"
JOB_ROLES_PATH = os.path.join(DATA_DIR, "job_roles.json")
COURSES_PATH = os.path.join(DATA_DIR, "courses.json")

if not os.path.exists(JOB_ROLES_PATH) or not os.path.exists(COURSES_PATH):
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
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

    # Save file
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    file.save(file_path)

    # Extract text based on file type
    if file.filename.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
    else:
        resume_text = extract_text_from_docx(file_path)

    if not resume_text.strip():
        return jsonify({'success': False, 'error': 'Could not extract text from resume'}), 500

    # Store resume text in session file
    session_id = f"session_{int(time.time())}"
    session_file = os.path.join(UPLOADS_DIR, f"{session_id}.txt")
    with open(session_file, 'w') as f:
        f.write(resume_text)

    return jsonify({'success': True, 'session_id': session_id})

@app.route('/extract-skills', methods=['POST'])
def extract_skills():
    session_id = request.json.get('session_id') if request.is_json else None
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400

    session_file = os.path.join(UPLOADS_DIR, f"{session_id}.txt")
    if not os.path.exists(session_file):
        return jsonify({'success': False, 'error': 'Session file not found'}), 404

    with open(session_file, 'r') as f:
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

    session_file = os.path.join(UPLOADS_DIR, f"{session_id}.txt")
    if not os.path.exists(session_file):
        return jsonify({'success': False, 'error': 'Session file not found'}), 404

    with open(session_file, 'r') as f:
        resume_text = f.read()

    try:
        start_time = time.time()
        result = run_pipeline(resume_text, role, log_execution=True)
        execution_time = time.time() - start_time

        # Format roadmap for frontend
        roadmap = []
        for phase in result.get('roadmap', []):
            phase_data = {
                'phase': phase.get('phase', 'Unknown Phase'),
                'skills': []
            }
            for item in phase.get('skills', phase.get('items', [])):
                course = item.get('course', {})
                phase_data['skills'].append({
                    'skill': item.get('skill', ''),
                    'course': {
                        'title': course.get('title', 'N/A'),
                        'platform': course.get('platform', 'N/A'),
                        'url': course.get('url', ''),
                        'reason': course.get('why', item.get('reason', 'N/A'))
                    }
                })
            roadmap.append(phase_data)

        response = {
            'success': True,
            'roadmap': roadmap,
            'resources': 'Personalized course recommendations based on your skill gaps and target role.'
        }
        return jsonify(response)
    except Exception as e:
        print(f"Roadmap generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)