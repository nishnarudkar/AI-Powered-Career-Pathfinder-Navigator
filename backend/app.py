from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
import PyPDF2
from docx import Document
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
from career_pathfinder_optimized import run_pipeline, run_pipeline_optimized, extract_skills_only
from career_logger import CareerPathfinderLogger
from role_readiness_agent import assess_role_readiness
import time

# Configure Flask app with proper template and static folders
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')

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

# Check for data files (use absolute path)
import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
DATA_DIR = os.path.join(project_root, "data")
JOB_ROLES_PATH = os.path.join(DATA_DIR, "job_roles.json")
COURSES_PATH = os.path.join(DATA_DIR, "courses.json")

print(f"🔍 Looking for data files:")
print(f"  - Current file: {__file__}")
print(f"  - Current dir: {current_dir}")
print(f"  - Project root: {project_root}")
print(f"  - Data dir: {DATA_DIR}")
print(f"  - Job roles: {JOB_ROLES_PATH} (exists: {os.path.exists(JOB_ROLES_PATH)})")
print(f"  - Courses: {COURSES_PATH} (exists: {os.path.exists(COURSES_PATH)})")

if os.path.exists(JOB_ROLES_PATH) and os.path.exists(COURSES_PATH):
    print(f"✅ Found curated data files!")
else:
    print(f"⚠️ Some curated data files not found, using AI-only mode")

def parse_course_info(course_string):
    """Parse course string to extract title, platform, and estimate duration"""
    if not course_string or course_string == 'N/A':
        return {
            'title': 'N/A',
            'platform': 'N/A',
            'duration': 'N/A',
            'url': ''
        }
    
    # Default duration mapping based on platform/course type
    duration_map = {
        'coursera': '4-6 weeks',
        'edx': '4-8 weeks', 
        'udemy': '10-15 hours',
        'youtube': '2-5 hours',
        'freecodecamp': '5-10 hours',
        'w3schools': '1-3 hours',
        'khan academy': '2-4 weeks',
        'ibm skillsbuild': '3-5 hours',
        'official documentation': '1-2 hours',
        'datacamp': '2-4 hours',
        'official': '1-2 hours',
        'microsoft learn': '2-4 hours',
        'google': '3-6 hours',
        'free book': '2-3 weeks',
        'tutorial': '1-3 hours'
    }
    
    title = course_string
    platform = 'Online'
    duration = '2-4 hours'  # default
    
    # Parse platform from course string
    if ' - ' in course_string:
        parts = course_string.split(' - ', 1)
        title = parts[0].strip()
        platform_part = parts[1].strip()
        
        # Extract platform (everything before parentheses if they exist)
        if ' (' in platform_part:
            platform = platform_part.split(' (')[0].strip()
        else:
            platform = platform_part
    
    # Determine duration based on platform
    platform_lower = platform.lower()
    for key, dur in duration_map.items():
        if key in platform_lower:
            duration = dur
            break
    
    # Special cases for course types
    if 'certification' in course_string.lower() or 'certificate' in course_string.lower():
        duration = '6-8 weeks'
    elif 'bootcamp' in course_string.lower():
        duration = '12-24 weeks'
    elif 'crash course' in course_string.lower():
        duration = '1-2 days'
    elif 'full course' in course_string.lower():
        duration = '8-12 hours'
    elif 'tutorial' in course_string.lower():
        duration = '1-3 hours'
    
    return {
        'title': title,
        'platform': platform,
        'duration': duration,
        'url': generate_course_url(title, platform)
    }

def generate_course_url(title, platform):
    """Generate course URLs based on platform and title"""
    platform_lower = platform.lower()
    title_lower = title.lower()
    
    # Platform-based URL patterns with specific course URLs
    if 'coursera' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.coursera.org/learn/python-crash-course'
        elif 'machine learning' in title_lower or 'ml' in title_lower:
            return 'https://www.coursera.org/specializations/machine-learning-introduction'
        elif 'data science' in title_lower:
            return 'https://www.coursera.org/specializations/data-science-python'
        elif 'statistics' in title_lower:
            return 'https://www.coursera.org/learn/inferential-statistics-intro'
        elif 'sql' in title_lower or 'database' in title_lower:
            return 'https://www.coursera.org/learn/intro-sql'
        elif 'deep learning' in title_lower:
            return 'https://www.coursera.org/specializations/deep-learning'
        elif 'tensorflow' in title_lower:
            return 'https://www.coursera.org/professional-certificates/tensorflow-in-practice'
        elif 'docker' in title_lower:
            return 'https://www.coursera.org/projects/docker-container-basics'
        elif 'kubernetes' in title_lower:
            return 'https://www.coursera.org/learn/google-kubernetes-engine'
        elif 'aws' in title_lower:
            return 'https://www.coursera.org/learn/aws-cloud-technical-essentials'
        elif 'azure' in title_lower:
            return 'https://www.coursera.org/learn/microsoft-azure-fundamentals-az-900'
        elif 'cybersecurity' in title_lower or 'security' in title_lower:
            return 'https://www.coursera.org/professional-certificates/google-cybersecurity'
        elif 'networking' in title_lower:
            return 'https://www.coursera.org/learn/computer-networking'
        elif 'product management' in title_lower or 'product strategy' in title_lower:
            return 'https://www.coursera.org/specializations/real-world-product-management'
        elif 'agile' in title_lower:
            return 'https://www.coursera.org/learn/agile-development-scrum'
        else:
            return f'https://www.coursera.org/search?query={title.replace(" ", "%20")}'
    
    elif 'udemy' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.udemy.com/course/complete-python-bootcamp/'
        elif 'machine learning' in title_lower:
            return 'https://www.udemy.com/course/machinelearning/'
        elif 'data science' in title_lower:
            return 'https://www.udemy.com/course/the-data-science-course-complete-data-science-bootcamp/'
        elif 'sql' in title_lower:
            return 'https://www.udemy.com/course/the-complete-sql-bootcamp/'
        elif 'docker' in title_lower:
            return 'https://www.udemy.com/course/docker-mastery/'
        elif 'kubernetes' in title_lower:
            return 'https://www.udemy.com/course/learn-kubernetes/'
        elif 'aws' in title_lower:
            return 'https://www.udemy.com/course/aws-certified-solutions-architect-associate/'
        elif 'azure' in title_lower:
            return 'https://www.udemy.com/course/microsoft-azure-administrator-az-104/'
        elif 'javascript' in title_lower:
            return 'https://www.udemy.com/course/the-complete-javascript-course/'
        elif 'react' in title_lower:
            return 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/'
        elif 'nodejs' in title_lower or 'node.js' in title_lower:
            return 'https://www.udemy.com/course/the-complete-nodejs-developer-course-2/'
        elif 'tensorflow' in title_lower:
            return 'https://www.udemy.com/course/complete-tensorflow-2-and-keras-deep-learning-bootcamp/'
        elif 'pytorch' in title_lower:
            return 'https://www.udemy.com/course/pytorch-for-deep-learning-with-python-bootcamp/'
        elif 'cybersecurity' in title_lower or 'security' in title_lower:
            return 'https://www.udemy.com/course/the-complete-cyber-security-course-hackers-exposed/'
        elif 'networking' in title_lower:
            return 'https://www.udemy.com/course/complete-networking-fundamentals-course-ccna-start/'
        elif 'linux' in title_lower:
            return 'https://www.udemy.com/course/linux-mastery/'
        elif 'git' in title_lower:
            return 'https://www.udemy.com/course/git-complete/'
        elif 'terraform' in title_lower:
            return 'https://www.udemy.com/course/terraform-beginner-to-advanced/'
        else:
            return f'https://www.udemy.com/courses/search/?q={title.replace(" ", "%20")}'
    
    elif 'khan academy' in platform_lower:
        if 'statistics' in title_lower:
            return 'https://www.khanacademy.org/math/ap-statistics'
        elif 'calculus' in title_lower:
            return 'https://www.khanacademy.org/math/calculus-1'
        elif 'algebra' in title_lower:
            return 'https://www.khanacademy.org/math/algebra'
        elif 'probability' in title_lower:
            return 'https://www.khanacademy.org/math/statistics-probability'
        else:
            return f'https://www.khanacademy.org/search?page_search_query={title.replace(" ", "%20")}'
    
    elif 'edx' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.edx.org/course/introduction-to-python-programming'
        elif 'data science' in title_lower:
            return 'https://www.edx.org/micromasters/mitx-statistics-and-data-science'
        elif 'machine learning' in title_lower:
            return 'https://www.edx.org/course/machine-learning'
        elif 'computer science' in title_lower:
            return 'https://www.edx.org/course/introduction-to-computer-science-and-programming-7'
        elif 'aws' in title_lower:
            return 'https://www.edx.org/course/introduction-to-cloud-infrastructure-technologies'
        elif 'cybersecurity' in title_lower or 'security' in title_lower:
            return 'https://www.edx.org/course/cybersecurity-fundamentals'
        else:
            return f'https://www.edx.org/search?q={title.replace(" ", "%20")}'
    
    elif 'youtube' in platform_lower:
        if 'python' in title_lower and 'beginner' in title_lower:
            return 'https://www.youtube.com/watch?v=_uQrJ0TkZlc'  # Python Tutorial for Beginners - Full Course
        elif 'machine learning' in title_lower:
            return 'https://www.youtube.com/watch?v=Gv9_4yMHFhI'  # Machine Learning Course - Crash Course
        elif 'data science' in title_lower:
            return 'https://www.youtube.com/watch?v=ua-CiDNNj30'  # Data Science Course 2024
        elif 'sql' in title_lower:
            return 'https://www.youtube.com/watch?v=HXV3zeQKqGY'  # SQL Tutorial - Full Database Course
        elif 'docker' in title_lower:
            return 'https://www.youtube.com/watch?v=fqMOX6JJhGo'  # Docker Tutorial for Beginners
        elif 'kubernetes' in title_lower:
            return 'https://www.youtube.com/watch?v=X48VuDVv0do'  # Kubernetes Tutorial for Beginners
        elif 'javascript' in title_lower:
            return 'https://www.youtube.com/watch?v=PkZNo7MFNFg'  # JavaScript Tutorial for Beginners
        elif 'react' in title_lower:
            return 'https://www.youtube.com/watch?v=bMknfKXIFA8'  # React Course - Beginner's Tutorial
        elif 'nodejs' in title_lower:
            return 'https://www.youtube.com/watch?v=RLtyhwFtXQA'  # Node.js Tutorial for Beginners
        elif 'aws' in title_lower:
            return 'https://www.youtube.com/watch?v=3hLmDS179YE'  # AWS Tutorial for Beginners
        elif 'tensorflow' in title_lower:
            return 'https://www.youtube.com/watch?v=tPYj3fFJGjk'  # TensorFlow 2.0 Complete Course
        elif 'cybersecurity' in title_lower:
            return 'https://www.youtube.com/watch?v=U_P23SqJaDc'  # Cybersecurity Full Course
        elif 'networking' in title_lower:
            return 'https://www.youtube.com/watch?v=qiQR5rTSshw'  # Computer Networking Course
        elif 'linux' in title_lower:
            return 'https://www.youtube.com/watch?v=sWbUDq4S6Y8'  # Linux Tutorial for Beginners
        else:
            return f'https://www.youtube.com/results?search_query={title.replace(" ", "+")}'
    
    elif 'freecodecamp' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.freecodecamp.org/learn/scientific-computing-with-python/'
        elif 'javascript' in title_lower:
            return 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/'
        elif 'data' in title_lower:
            return 'https://www.freecodecamp.org/learn/data-analysis-with-python/'
        elif 'machine learning' in title_lower:
            return 'https://www.freecodecamp.org/learn/machine-learning-with-python/'
        elif 'responsive web' in title_lower or 'html' in title_lower or 'css' in title_lower:
            return 'https://www.freecodecamp.org/learn/responsive-web-design/'
        elif 'backend' in title_lower or 'apis' in title_lower:
            return 'https://www.freecodecamp.org/learn/back-end-development-and-apis/'
        else:
            return f'https://www.freecodecamp.org/news/search/?query={title.replace(" ", "%20")}'
    
    elif 'datacamp' in platform_lower:
        if 'python' in title_lower and 'intro' in title_lower:
            return 'https://www.datacamp.com/courses/intro-to-python-for-data-science'
        elif 'sql' in title_lower and 'intro' in title_lower:
            return 'https://www.datacamp.com/courses/introduction-to-sql'
        elif 'machine learning' in title_lower:
            return 'https://www.datacamp.com/courses/supervised-learning-with-scikit-learn'
        elif 'pandas' in title_lower:
            return 'https://www.datacamp.com/courses/data-manipulation-with-pandas'
        elif 'numpy' in title_lower:
            return 'https://www.datacamp.com/courses/introduction-to-numpy'
        elif 'data visualization' in title_lower:
            return 'https://www.datacamp.com/courses/introduction-to-data-visualization-with-matplotlib'
        elif 'statistics' in title_lower:
            return 'https://www.datacamp.com/courses/statistical-thinking-in-python-part-1'
        else:
            return f'https://www.datacamp.com/search?q={title.replace(" ", "%20")}'
    
    elif 'ibm skillsbuild' in platform_lower or 'ibm' in platform_lower:
        if 'data science' in title_lower:
            return 'https://skillsbuild.org/students/course-catalog/data-science'
        elif 'ai' in title_lower or 'artificial intelligence' in title_lower:
            return 'https://skillsbuild.org/students/course-catalog/artificial-intelligence'
        elif 'cybersecurity' in title_lower:
            return 'https://skillsbuild.org/students/course-catalog/cybersecurity'
        elif 'cloud' in title_lower:
            return 'https://skillsbuild.org/students/course-catalog/cloud-computing'
        else:
            return f'https://skillsbuild.org/students/course-catalog'
    
    elif 'w3schools' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.w3schools.com/python/default.asp'
        elif 'javascript' in title_lower:
            return 'https://www.w3schools.com/js/default.asp'
        elif 'html' in title_lower:
            return 'https://www.w3schools.com/html/default.asp'
        elif 'css' in title_lower:
            return 'https://www.w3schools.com/css/default.asp'
        elif 'sql' in title_lower:
            return 'https://www.w3schools.com/sql/default.asp'
        elif 'react' in title_lower:
            return 'https://www.w3schools.com/react/default.asp'
        elif 'nodejs' in title_lower:
            return 'https://www.w3schools.com/nodejs/default.asp'
        else:
            return f'https://www.w3schools.com/{title.lower().replace(" ", "")}/default.asp'
    
    elif 'microsoft learn' in platform_lower:
        if 'azure fundamentals' in title_lower:
            return 'https://docs.microsoft.com/en-us/learn/paths/azure-fundamentals/'
        elif 'azure' in title_lower and 'admin' in title_lower:
            return 'https://docs.microsoft.com/en-us/learn/paths/az-104-administrator-prerequisites/'
        elif 'python' in title_lower:
            return 'https://docs.microsoft.com/en-us/learn/paths/beginner-python/'
        elif 'ai' in title_lower or 'artificial intelligence' in title_lower:
            return 'https://docs.microsoft.com/en-us/learn/paths/get-started-with-artificial-intelligence-on-azure/'
        elif 'data science' in title_lower:
            return 'https://docs.microsoft.com/en-us/learn/paths/introduction-to-data-science-in-azure/'
        else:
            return f'https://docs.microsoft.com/en-us/learn/search/?terms={title.replace(" ", "%20")}'
    
    elif 'google' in platform_lower or 'google developers' in platform_lower:
        if 'machine learning crash course' in title_lower:
            return 'https://developers.google.com/machine-learning/crash-course'
        elif 'tensorflow' in title_lower:
            return 'https://www.tensorflow.org/learn'
        elif 'cloud' in title_lower:
            return 'https://cloud.google.com/training/courses'
        elif 'android' in title_lower:
            return 'https://developer.android.com/courses'
        else:
            return f'https://developers.google.com/search/results?q={title.replace(" ", "%20")}'
    
    elif 'pluralsight' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.pluralsight.com/courses/python-fundamentals'
        elif 'javascript' in title_lower:
            return 'https://www.pluralsight.com/courses/javascript-fundamentals'
        elif 'docker' in title_lower:
            return 'https://www.pluralsight.com/courses/docker-fundamentals'
        elif 'kubernetes' in title_lower:
            return 'https://www.pluralsight.com/courses/kubernetes-installation-configuration-fundamentals'
        elif 'aws' in title_lower:
            return 'https://www.pluralsight.com/courses/aws-certified-solutions-architect-associate'
        else:
            return f'https://www.pluralsight.com/search?q={title.replace(" ", "%20")}'
    
    elif 'linkedin learning' in platform_lower:
        if 'python' in title_lower:
            return 'https://www.linkedin.com/learning/python-essential-training-2'
        elif 'data science' in title_lower:
            return 'https://www.linkedin.com/learning/data-science-foundations-fundamentals-5'
        elif 'machine learning' in title_lower:
            return 'https://www.linkedin.com/learning/machine-learning-foundations-a-case-study-approach'
        elif 'project management' in title_lower:
            return 'https://www.linkedin.com/learning/project-management-foundations-4'
        else:
            return f'https://www.linkedin.com/learning/search?keywords={title.replace(" ", "%20")}'
    
    # Generic fallbacks for skill-based URLs with better search
    elif 'python' in title_lower:
        return 'https://www.python.org/about/gettingstarted/'
    elif 'machine learning' in title_lower or 'ml' in title_lower:
        return 'https://www.coursera.org/specializations/machine-learning-introduction'
    elif 'data science' in title_lower:
        return 'https://www.kaggle.com/learn/intro-to-machine-learning'
    elif 'sql' in title_lower:
        return 'https://sqlbolt.com/'
    elif 'docker' in title_lower:
        return 'https://docs.docker.com/get-started/'
    elif 'kubernetes' in title_lower:
        return 'https://kubernetes.io/docs/tutorials/kubernetes-basics/'
    elif 'git' in title_lower:
        return 'https://learngitbranching.js.org/'
    elif 'linux' in title_lower:
        return 'https://linuxjourney.com/'
    elif 'javascript' in title_lower:
        return 'https://javascript.info/'
    elif 'react' in title_lower:
        return 'https://react.dev/learn'
    elif 'nodejs' in title_lower or 'node.js' in title_lower:
        return 'https://nodejs.org/en/learn/getting-started/introduction-to-nodejs'
    elif 'aws' in title_lower:
        return 'https://aws.amazon.com/getting-started/'
    elif 'azure' in title_lower:
        return 'https://docs.microsoft.com/en-us/learn/azure/'
    elif 'tensorflow' in title_lower:
        return 'https://www.tensorflow.org/tutorials'
    elif 'pytorch' in title_lower:
        return 'https://pytorch.org/tutorials/beginner/basics/intro.html'
    elif 'cybersecurity' in title_lower or 'security' in title_lower:
        return 'https://www.cybrary.it/course/comptia-security-plus'
    elif 'networking' in title_lower:
        return 'https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html'
    elif 'agile' in title_lower:
        return 'https://www.scrum.org/learning-series/what-is-scrum'
    elif 'product management' in title_lower:
        return 'https://www.productschool.com/product-management-101/'
    
    # Default fallback with better search
    return f'https://www.google.com/search?q="{title}"+"online+course"'

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
    with open(session_file, 'w', encoding='utf-8') as f:
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

    with open(session_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    try:
        start_time = time.time()
        # Use fast skill extraction instead of full pipeline
        result = extract_skills_only(resume_text)
        execution_time = time.time() - start_time
        logger.log_execution(resume_text, "Skill Extraction", result, execution_time)
        return jsonify({'success': True, 'skills': result.get('extracted_skills', [])})
    except Exception as e:
        print(f"Skill extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/create-manual-session', methods=['POST'])
def create_manual_session():
    """Create a session for manual skills entry without resume upload"""
    data = request.get_json()
    skills_input = data.get('skills', '')
    
    # Parse space-separated skills
    if isinstance(skills_input, str):
        # Split by spaces and clean up
        skills_list = [skill.strip() for skill in skills_input.split() if skill.strip()]
    else:
        skills_list = skills_input if isinstance(skills_input, list) else []
    
    # Create a dummy resume text with the manual skills
    resume_text = f"Manual skills entry:\nSkills: {', '.join(skills_list)}\nExperience: User provided skills manually."
    
    # Create session file
    session_id = f"manual_session_{int(time.time())}"
    session_file = os.path.join(UPLOADS_DIR, f"{session_id}.txt")
    with open(session_file, 'w', encoding='utf-8') as f:
        f.write(resume_text)
    
    return jsonify({
        'success': True, 
        'session_id': session_id,
        'skills': skills_list
    })

@app.route('/assess-target-role-readiness', methods=['POST'])
def assess_target_role_readiness():
    """Assess user readiness for a specific target role only"""
    data = request.get_json()
    skills = data.get('skills', [])
    target_role = data.get('target_role', '')
    force_refresh = data.get('force_refresh', False)
    
    if not skills:
        return jsonify({'success': False, 'error': 'No skills provided'}), 400
    if not target_role:
        return jsonify({'success': False, 'error': 'No target role specified'}), 400
    
    try:
        start_time = time.time()
        
        # Use the single role readiness agent
        from role_readiness_agent import assess_single_role_readiness
        readiness_result = assess_single_role_readiness(skills, target_role, force_refresh)
        
        # Also perform industry readiness evaluation
        role_profile = get_role_profile(target_role)
        industry_evaluation = None
        
        if role_profile and any(role_profile.values()):  # Check if role profile exists
            # Calculate industry readiness evaluation
            core_technical_skills = role_profile.get('core_technical_skills', [])
            other_technical_skills = role_profile.get('other_technical_skills', [])
            soft_skills = role_profile.get('soft_skills', [])
            
            # Calculate scores for each category
            core_score = calculate_skill_category_score(skills, core_technical_skills)
            other_score = calculate_skill_category_score(skills, other_technical_skills)
            soft_score = calculate_skill_category_score(skills, soft_skills)
            
            # Calculate weighted overall score (60% core, 30% other, 10% soft)
            overall_score = (core_score * 0.6) + (other_score * 0.3) + (soft_score * 0.1)
            
            # Determine readiness level
            if overall_score >= 0.8:
                readiness_level = "Ready / Strong fit"
            elif overall_score >= 0.6:
                readiness_level = "Workable with targeted upskilling"
            else:
                readiness_level = "Needs foundation"
            
            # Identify missing critical skills
            missing_critical_skills = identify_missing_critical_skills(
                skills, core_technical_skills + other_technical_skills
            )
            
            # Generate recommendations
            recommendations = generate_skill_recommendations(missing_critical_skills)
            
            # Identify strengths
            strengths = identify_candidate_strengths(skills, core_technical_skills + other_technical_skills)
            
            # Create breakdown
            breakdown = [
                {
                    "category": "Core Technical Skills (60%)",
                    "score": round(core_score, 2),
                    "present_skills": get_present_skills(skills, core_technical_skills),
                    "missing_critical": get_missing_skills(skills, core_technical_skills),
                    "notes": generate_category_notes(core_score, "core technical skills")
                },
                {
                    "category": "Other Technical Skills (30%)",
                    "score": round(other_score, 2),
                    "present_skills": get_present_skills(skills, other_technical_skills),
                    "missing_critical": get_missing_skills(skills, other_technical_skills),
                    "notes": generate_category_notes(other_score, "other technical skills")
                },
                {
                    "category": "Soft Skills (10%)",
                    "score": round(soft_score, 2),
                    "notes": "Assessment based on inferred capabilities from experience and projects"
                }
            ]
            
            industry_evaluation = {
                "overall_score": round(overall_score, 2),
                "readiness_level": readiness_level,
                "breakdown": breakdown,
                "missing_critical_skills": missing_critical_skills,
                "recommendations": recommendations,
                "strengths": strengths,
                "next_steps": generate_next_steps(overall_score, target_role, len(missing_critical_skills))
            }
        
        execution_time = time.time() - start_time
        
        # Log the assessment
        logger.log_execution(
            input_text=f"Skills: {', '.join(skills)}",
            target_role=f"Target Role Assessment: {target_role}",
            result=readiness_result,
            execution_time=execution_time
        )
        
        response = {
            'success': True,
            'role_readiness': readiness_result,
            'industry_evaluation': industry_evaluation,
            'assessment_time': round(execution_time, 3)
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Target role readiness assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_skill_category_score(user_skills, required_skills):
    """Calculate score for a skill category based on presence of required skills"""
    if not required_skills:
        return 0.0
    
    user_skills_lower = [skill.lower().replace('-', '').replace('_', '') for skill in user_skills]
    present_count = 0
    
    for skill_req in required_skills:
        skill_name = skill_req.get('skill', '').lower().replace('-', '').replace('_', '')
        if skill_name in user_skills_lower:
            present_count += 1
    
    return present_count / len(required_skills)

def identify_missing_critical_skills(user_skills, required_skills):
    """Identify missing critical skills with severity assessment"""
    user_skills_lower = [skill.lower().replace('-', '').replace('_', '') for skill in user_skills]
    missing_skills = []
    
    for i, skill_req in enumerate(required_skills):
        skill_name = skill_req.get('skill', '')
        required_level = skill_req.get('required_level', 2)
        
        skill_name_normalized = skill_name.lower().replace('-', '').replace('_', '')
        if skill_name_normalized not in user_skills_lower:
            gap_severity = "High" if required_level >= 3 else "Medium"
            missing_skills.append({
                "skill": skill_name,
                "required_level": required_level,
                "current_level": 0,
                "gap_severity": gap_severity,
                "learning_priority": i + 1
            })
    
    return missing_skills[:5]  # Return top 5 missing skills

def generate_skill_recommendations(missing_skills):
    """Generate actionable recommendations for missing skills"""
    recommendations = []
    
    for i, skill in enumerate(missing_skills[:3]):  # Top 3 recommendations
        skill_name = skill['skill']
        required_level = skill['required_level']
        
        # Estimate timeline based on skill complexity
        if required_level >= 3:
            timeline = "2-4 weeks"
            hours = "15-25 hours"
        else:
            timeline = "1-2 weeks"
            hours = "8-15 hours"
        
        recommendations.append({
            "priority": i + 1,
            "skill": skill_name,
            "action": f"Complete foundational {skill_name} training ({hours})",
            "timeline": timeline,
            "impact": get_skill_impact_description(skill_name, required_level)
        })
    
    return recommendations

def get_skill_impact_description(skill_name, required_level):
    """Get impact description for a skill"""
    impact_map = {
        'git': "Essential for version control and collaboration",
        'jenkins': "Critical for DevOps automation workflows", 
        'docker': "Essential for containerization and deployment",
        'kubernetes': "Critical for container orchestration",
        'linux': "Fundamental for system administration",
        'bash': "Essential for system administration and automation",
        'python': "Versatile programming for automation and development",
        'ci-cd': "Critical for automated deployment pipelines",
        'terraform': "Essential for infrastructure as code",
        'aws': "Important for cloud infrastructure management",
        'monitoring': "Critical for system observability and reliability"
    }
    
    return impact_map.get(skill_name.lower(), f"Important skill for {skill_name} proficiency")

def identify_candidate_strengths(user_skills, required_skills):
    """Identify candidate's existing strengths"""
    user_skills_lower = [skill.lower().replace('-', '').replace('_', '') for skill in user_skills]
    strengths = []
    
    strength_descriptions = {
        'docker': "Strong containerization experience",
        'kubernetes': "Container orchestration proficiency", 
        'aws': "Cloud platform experience",
        'terraform': "Infrastructure as Code proficiency",
        'ci-cd': "Continuous integration/deployment knowledge",
        'python': "Programming and automation capabilities",
        'linux': "System administration foundation",
        'monitoring': "System observability skills",
        'prometheus': "Advanced monitoring and observability",
        'grafana': "Data visualization and monitoring",
        'ansible': "Configuration management expertise"
    }
    
    for skill_req in required_skills:
        skill_name = skill_req.get('skill', '')
        skill_normalized = skill_name.lower().replace('-', '').replace('_', '')
        
        if skill_normalized in user_skills_lower:
            description = strength_descriptions.get(skill_name.lower(), f"Experience with {skill_name}")
            strengths.append(description)
    
    return strengths

def get_present_skills(user_skills, required_skills):
    """Get list of present skills from required skills"""
    user_skills_lower = [skill.lower().replace('-', '').replace('_', '') for skill in user_skills]
    present = []
    
    for skill_req in required_skills:
        skill_name = skill_req.get('skill', '')
        skill_normalized = skill_name.lower().replace('-', '').replace('_', '')
        if skill_normalized in user_skills_lower:
            present.append(skill_name)
    
    return present

def get_missing_skills(user_skills, required_skills):
    """Get list of missing skills from required skills"""
    user_skills_lower = [skill.lower().replace('-', '').replace('_', '') for skill in user_skills]
    missing = []
    
    for skill_req in required_skills:
        skill_name = skill_req.get('skill', '')
        skill_normalized = skill_name.lower().replace('-', '').replace('_', '')
        if skill_normalized not in user_skills_lower:
            missing.append(skill_name)
    
    return missing

def generate_category_notes(score, category_name):
    """Generate notes for a skill category based on score"""
    if score >= 0.8:
        return f"Excellent {category_name} foundation with most required skills present"
    elif score >= 0.6:
        return f"Good {category_name} base with some gaps to address"
    elif score >= 0.4:
        return f"Moderate {category_name} foundation but significant gaps exist"
    else:
        return f"Limited {category_name} experience, foundational learning needed"

def generate_next_steps(overall_score, target_role, missing_skills_count):
    """Generate next steps recommendation"""
    if overall_score >= 0.8:
        return f"Strong candidate for {target_role}. Focus on advanced skills and specialization."
    elif overall_score >= 0.6:
        months = max(1, missing_skills_count // 2)
        return f"Solid foundation for {target_role}. Address key skill gaps with {months}-{months+1} months of targeted learning."
    else:
        months = max(2, missing_skills_count // 2)
        return f"Foundational skills needed for {target_role}. Plan {months}-{months+2} months of comprehensive skill development."

@app.route('/assess-role-readiness', methods=['POST'])
def assess_role_readiness_endpoint():
    """Assess user readiness for various job roles based on current skills"""
    data = request.get_json()
    skills = data.get('skills', [])
    force_refresh = data.get('force_refresh', False)
    
    if not skills:
        return jsonify({'success': False, 'error': 'No skills provided'}), 400
    
    try:
        start_time = time.time()
        
        # Use the role readiness agent
        readiness_result = assess_role_readiness(skills, force_refresh)
        execution_time = time.time() - start_time
        
        # Log the assessment
        logger.log_execution(
            input_text=f"Skills: {', '.join(skills)}",
            target_role="Role Assessment",
            result=readiness_result,
            execution_time=execution_time
        )
        
        response = {
            'success': True,
            'role_readiness': readiness_result,
            'assessment_time': round(execution_time, 3)
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Role readiness assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-role-summaries', methods=['POST'])
def generate_role_summaries():
    """Generate concise UI summaries for role readiness assessments"""
    data = request.get_json()
    role_matches = data.get('role_matches', [])
    
    if not role_matches:
        return jsonify({'success': False, 'error': 'No role matches provided'}), 400
    
    try:
        # Create agent instance
        from role_readiness_agent import RoleReadinessAgent
        agent = RoleReadinessAgent()
        
        # Generate summaries for each role
        summaries = {}
        for role_match in role_matches:
            role_name = role_match.get('role_name', '')
            if role_name:
                summaries[role_name] = agent.generate_role_summary(role_match)
        
        return jsonify({
            'success': True,
            'summaries': summaries
        })
        
    except Exception as e:
        print(f"Role summary generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_role_profile(target_role):
    """Get the role profile for industry readiness evaluation"""
    role_profiles = {
        "devops-engineer": {
            "core_technical_skills": [
                {"skill": "linux", "required_level": 3, "weight": 0.6},
                {"skill": "docker", "required_level": 3, "weight": 0.6},
                {"skill": "kubernetes", "required_level": 2, "weight": 0.6},
                {"skill": "git", "required_level": 3, "weight": 0.6},
                {"skill": "ci-cd", "required_level": 3, "weight": 0.6},
                {"skill": "jenkins", "required_level": 2, "weight": 0.6},
                {"skill": "terraform", "required_level": 2, "weight": 0.6},
                {"skill": "aws", "required_level": 2, "weight": 0.6},
                {"skill": "bash", "required_level": 2, "weight": 0.6},
                {"skill": "monitoring", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "ansible", "required_level": 2, "weight": 0.3},
                {"skill": "python", "required_level": 2, "weight": 0.3},
                {"skill": "azure", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "collaboration", "required_level": 2, "weight": 0.1},
                {"skill": "problem-solving", "required_level": 2, "weight": 0.1}
            ]
        },
        "data-scientist": {
            "core_technical_skills": [
                {"skill": "python", "required_level": 3, "weight": 0.6},
                {"skill": "sql", "required_level": 3, "weight": 0.6},
                {"skill": "statistics", "required_level": 3, "weight": 0.6},
                {"skill": "machine-learning", "required_level": 3, "weight": 0.6},
                {"skill": "pandas", "required_level": 3, "weight": 0.6},
                {"skill": "numpy", "required_level": 2, "weight": 0.6},
                {"skill": "scikit-learn", "required_level": 2, "weight": 0.6},
                {"skill": "data-visualization", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "jupyter", "required_level": 2, "weight": 0.3},
                {"skill": "tensorflow", "required_level": 2, "weight": 0.3},
                {"skill": "pytorch", "required_level": 2, "weight": 0.3},
                {"skill": "deep-learning", "required_level": 2, "weight": 0.3},
                {"skill": "r", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "analytical-thinking", "required_level": 3, "weight": 0.1},
                {"skill": "communication", "required_level": 2, "weight": 0.1}
            ]
        },
        "full-stack-developer": {
            "core_technical_skills": [
                {"skill": "javascript", "required_level": 3, "weight": 0.6},
                {"skill": "html", "required_level": 3, "weight": 0.6},
                {"skill": "css", "required_level": 3, "weight": 0.6},
                {"skill": "react", "required_level": 3, "weight": 0.6},
                {"skill": "nodejs", "required_level": 3, "weight": 0.6},
                {"skill": "sql", "required_level": 2, "weight": 0.6},
                {"skill": "git", "required_level": 2, "weight": 0.6},
                {"skill": "rest-api", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "express", "required_level": 2, "weight": 0.3},
                {"skill": "mongodb", "required_level": 2, "weight": 0.3},
                {"skill": "docker", "required_level": 2, "weight": 0.3},
                {"skill": "aws", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "problem-solving", "required_level": 3, "weight": 0.1},
                {"skill": "creativity", "required_level": 2, "weight": 0.1}
            ]
        },
        "ml-engineer": {
            "core_technical_skills": [
                {"skill": "python", "required_level": 3, "weight": 0.6},
                {"skill": "machine-learning", "required_level": 3, "weight": 0.6},
                {"skill": "tensorflow", "required_level": 3, "weight": 0.6},
                {"skill": "pytorch", "required_level": 2, "weight": 0.6},
                {"skill": "deep-learning", "required_level": 3, "weight": 0.6},
                {"skill": "docker", "required_level": 2, "weight": 0.6},
                {"skill": "sql", "required_level": 2, "weight": 0.6},
                {"skill": "git", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "kubernetes", "required_level": 2, "weight": 0.3},
                {"skill": "linux", "required_level": 2, "weight": 0.3},
                {"skill": "aws", "required_level": 2, "weight": 0.3},
                {"skill": "mlops", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "analytical-thinking", "required_level": 3, "weight": 0.1},
                {"skill": "collaboration", "required_level": 2, "weight": 0.1}
            ]
        },
        "ai-engineer": {
            "core_technical_skills": [
                {"skill": "python", "required_level": 3, "weight": 0.6},
                {"skill": "deep-learning", "required_level": 3, "weight": 0.6},
                {"skill": "tensorflow", "required_level": 3, "weight": 0.6},
                {"skill": "pytorch", "required_level": 2, "weight": 0.6},
                {"skill": "machine-learning", "required_level": 3, "weight": 0.6},
                {"skill": "neural-networks", "required_level": 3, "weight": 0.6},
                {"skill": "computer-vision", "required_level": 2, "weight": 0.6},
                {"skill": "nlp", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "transformers", "required_level": 2, "weight": 0.3},
                {"skill": "llm", "required_level": 2, "weight": 0.3},
                {"skill": "hugging-face", "required_level": 2, "weight": 0.3},
                {"skill": "gpu-computing", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "research-skills", "required_level": 3, "weight": 0.1},
                {"skill": "innovation", "required_level": 2, "weight": 0.1}
            ]
        },
        "cloud-architect": {
            "core_technical_skills": [
                {"skill": "aws", "required_level": 3, "weight": 0.6},
                {"skill": "azure", "required_level": 2, "weight": 0.6},
                {"skill": "docker", "required_level": 3, "weight": 0.6},
                {"skill": "kubernetes", "required_level": 3, "weight": 0.6},
                {"skill": "terraform", "required_level": 2, "weight": 0.6},
                {"skill": "linux", "required_level": 3, "weight": 0.6},
                {"skill": "networking", "required_level": 2, "weight": 0.6},
                {"skill": "security", "required_level": 2, "weight": 0.6},
                {"skill": "monitoring", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "gcp", "required_level": 2, "weight": 0.3},
                {"skill": "ansible", "required_level": 2, "weight": 0.3},
                {"skill": "jenkins", "required_level": 2, "weight": 0.3},
                {"skill": "python", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "system-design", "required_level": 3, "weight": 0.1},
                {"skill": "leadership", "required_level": 2, "weight": 0.1}
            ]
        },
        "cybersecurity-analyst": {
            "core_technical_skills": [
                {"skill": "security", "required_level": 3, "weight": 0.6},
                {"skill": "networking", "required_level": 3, "weight": 0.6},
                {"skill": "linux", "required_level": 2, "weight": 0.6},
                {"skill": "windows", "required_level": 2, "weight": 0.6},
                {"skill": "incident-response", "required_level": 2, "weight": 0.6},
                {"skill": "vulnerability-assessment", "required_level": 2, "weight": 0.6},
                {"skill": "penetration-testing", "required_level": 2, "weight": 0.6},
                {"skill": "siem", "required_level": 2, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "python", "required_level": 2, "weight": 0.3},
                {"skill": "powershell", "required_level": 2, "weight": 0.3},
                {"skill": "forensics", "required_level": 2, "weight": 0.3},
                {"skill": "compliance", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "attention-to-detail", "required_level": 3, "weight": 0.1},
                {"skill": "critical-thinking", "required_level": 3, "weight": 0.1}
            ]
        },
        "product-manager": {
            "core_technical_skills": [
                {"skill": "product-strategy", "required_level": 3, "weight": 0.6},
                {"skill": "user-research", "required_level": 3, "weight": 0.6},
                {"skill": "data-analysis", "required_level": 2, "weight": 0.6},
                {"skill": "agile", "required_level": 3, "weight": 0.6},
                {"skill": "roadmapping", "required_level": 3, "weight": 0.6},
                {"skill": "market-research", "required_level": 2, "weight": 0.6},
                {"skill": "stakeholder-management", "required_level": 3, "weight": 0.6}
            ],
            "other_technical_skills": [
                {"skill": "sql", "required_level": 2, "weight": 0.3},
                {"skill": "analytics-tools", "required_level": 2, "weight": 0.3},
                {"skill": "wireframing", "required_level": 2, "weight": 0.3},
                {"skill": "a-b-testing", "required_level": 2, "weight": 0.3}
            ],
            "soft_skills": [
                {"skill": "communication", "required_level": 3, "weight": 0.1},
                {"skill": "leadership", "required_level": 3, "weight": 0.1},
                {"skill": "empathy", "required_level": 2, "weight": 0.1}
            ]
        }
    }
    
    return role_profiles.get(target_role, {
        "core_technical_skills": [],
        "other_technical_skills": [],
        "soft_skills": []
    })

@app.route('/select-target-role', methods=['POST'])
def select_target_role():
    """Select a target role from role readiness assessment for focused roadmap generation"""
    data = request.get_json()
    selected_role = data.get('role_name', '')
    session_id = data.get('session_id', '')
    
    if not selected_role:
        return jsonify({'success': False, 'error': 'No role selected'}), 400
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400
    
    # Store the selected role in the session or return success
    # This endpoint can be used to trigger a new roadmap generation
    return jsonify({
        'success': True,
        'selected_role': selected_role,
        'message': f'Target role set to {selected_role}. You can now generate a focused roadmap.'
    })

@app.route('/evaluate-industry-readiness', methods=['POST'])
def evaluate_industry_readiness():
    """
    Industry Readiness Evaluator Endpoint
    
    Evaluates candidate readiness for a specific role using structured assessment
    following the JSON schema requirements for Industry Readiness Evaluation.
    """
    data = request.get_json()
    
    # Validate input according to JSON schema
    target_role = data.get('target_role', '')
    extracted_skills = data.get('extracted_skills', [])
    role_profile = data.get('role_profile', {})
    
    if not target_role:
        return jsonify({'success': False, 'error': 'target_role is required'}), 400
    if not extracted_skills:
        return jsonify({'success': False, 'error': 'extracted_skills array is required'}), 400
    if not role_profile:
        return jsonify({'success': False, 'error': 'role_profile is required'}), 400
    
    try:
        start_time = time.time()
        
        # Get role profile components
        core_technical_skills = role_profile.get('core_technical_skills', [])
        other_technical_skills = role_profile.get('other_technical_skills', [])
        soft_skills = role_profile.get('soft_skills', [])
        
        # Calculate scores for each category
        core_score = calculate_skill_category_score(extracted_skills, core_technical_skills)
        other_score = calculate_skill_category_score(extracted_skills, other_technical_skills)
        soft_score = calculate_skill_category_score(extracted_skills, soft_skills)
        
        # Calculate weighted overall score (60% core, 30% other, 10% soft)
        overall_score = (core_score * 0.6) + (other_score * 0.3) + (soft_score * 0.1)
        
        # Determine readiness level
        if overall_score >= 0.8:
            readiness_level = "Ready / Strong fit"
        elif overall_score >= 0.6:
            readiness_level = "Workable with targeted upskilling"
        else:
            readiness_level = "Needs foundation"
        
        # Identify missing critical skills
        missing_critical_skills = identify_missing_critical_skills(
            extracted_skills, core_technical_skills + other_technical_skills
        )
        
        # Generate recommendations
        recommendations = generate_skill_recommendations(missing_critical_skills)
        
        # Identify strengths
        strengths = identify_candidate_strengths(extracted_skills, core_technical_skills + other_technical_skills)
        
        # Create breakdown
        breakdown = [
            {
                "category": "Core Technical Skills (60%)",
                "score": round(core_score, 2),
                "present_skills": get_present_skills(extracted_skills, core_technical_skills),
                "missing_critical": get_missing_skills(extracted_skills, core_technical_skills),
                "notes": generate_category_notes(core_score, "core technical skills")
            },
            {
                "category": "Other Technical Skills (30%)",
                "score": round(other_score, 2),
                "present_skills": get_present_skills(extracted_skills, other_technical_skills),
                "missing_critical": get_missing_skills(extracted_skills, other_technical_skills),
                "notes": generate_category_notes(other_score, "other technical skills")
            },
            {
                "category": "Soft Skills (10%)",
                "score": round(soft_score, 2),
                "notes": "Assessment based on inferred capabilities from experience and projects"
            }
        ]
        
        # Construct response according to JSON schema
        response = {
            "success": True,
            "industry_readiness": {
                "overall_score": round(overall_score, 2),
                "readiness_level": readiness_level
            },
            "breakdown": breakdown,
            "missing_critical_skills": missing_critical_skills,
            "recommendations": recommendations,
            "strengths": strengths,
            "next_steps": generate_next_steps(overall_score, target_role, len(missing_critical_skills)),
            "assessment_time": round(time.time() - start_time, 3)
        }
        
        # Log the assessment
        logger.log_execution(
            input_text=f"Skills: {', '.join(extracted_skills)}, Role: {target_role}",
            target_role="Industry Readiness Assessment",
            result=response,
            execution_time=time.time() - start_time
        )
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Industry readiness assessment error: {e}")
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

    with open(session_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    try:
        start_time = time.time()
        
        # Use pipeline without force refresh functionality
        result = run_pipeline_optimized(resume_text, role, log_execution=True)
        execution_time = time.time() - start_time
        
        # Debug: Check what we got from run_pipeline
        print(f"Debug: run_pipeline returned type: {type(result)}")
        print(f"Debug: Performance summary: {result.get('performance_summary', {})}")
        
        # Handle case where result might be a string (error case)
        if isinstance(result, str):
            return jsonify({'success': False, 'error': f'Pipeline returned error: {result}'}), 500
            
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            return jsonify({'success': False, 'error': f'Unexpected result type: {type(result)}'}), 500

        # Format roadmap for frontend with better error handling
        roadmap = []
        roadmap_data = result.get('roadmap', [])
        
        # Debug: Print the roadmap structure
        print(f"Debug: roadmap type: {type(roadmap_data)}")
        print(f"Debug: roadmap length: {len(roadmap_data) if isinstance(roadmap_data, list) else 'N/A'}")
        
        if isinstance(roadmap_data, list):
            for i, phase in enumerate(roadmap_data):
                print(f"Debug: phase {i} type: {type(phase)}")
                
                # Handle case where phase might be a string instead of dict
                if isinstance(phase, str):
                    phase_data = {
                        'phase': f'Phase {i+1}',
                        'skills': [{'skill': phase, 'course': {'title': 'N/A', 'platform': 'N/A', 'duration': 'N/A', 'url': '', 'reason': 'N/A'}, 'est_hours': 10}],
                        'phase_total_hours': 10,
                        'phase_time_frame': 'Estimated time: 10 hours (~1.25 weeks at 8 hrs/week)'
                    }
                elif isinstance(phase, dict):
                    phase_data = {
                        'phase': phase.get('phase', f'Phase {i+1}'),
                        'skills': [],
                        'phase_total_hours': phase.get('phase_total_hours', 0),
                        'phase_time_frame': phase.get('phase_time_frame', 'Time estimates not available')
                    }
                    
                    skills_data = phase.get('skills', phase.get('items', []))
                    for j, item in enumerate(skills_data):
                        print(f"Debug: skill item {j} type: {type(item)}")
                        
                        if isinstance(item, str):
                            # Handle case where item is just a skill string
                            phase_data['skills'].append({
                                'skill': item,
                                'course': {
                                    'title': 'N/A',
                                    'platform': 'N/A', 
                                    'duration': 'N/A',
                                    'url': '',
                                    'reason': 'N/A'
                                },
                                'est_hours': 10
                            })
                        elif isinstance(item, dict):
                            # Handle normal case where item is a dict
                            course = item.get('course', {})
                            
                            # Handle case where course might be a string
                            if isinstance(course, str):
                                parsed_course = parse_course_info(course)
                                course_info = {
                                    'title': parsed_course['title'],
                                    'platform': parsed_course['platform'],
                                    'duration': parsed_course['duration'],
                                    'url': parsed_course['url'],
                                    'reason': item.get('reason', 'N/A')
                                }
                            elif isinstance(course, dict):
                                # If it's already a dict, parse the title for better platform/duration info
                                title = course.get('title', 'N/A')
                                parsed_course = parse_course_info(title)
                                course_info = {
                                    'title': parsed_course['title'],
                                    'platform': course.get('platform', parsed_course['platform']),
                                    'duration': course.get('duration', parsed_course['duration']),
                                    'url': course.get('url', ''),
                                    'reason': course.get('why', item.get('reason', 'N/A'))
                                }
                            else:
                                parsed_course = parse_course_info(str(course) if course else 'N/A')
                                course_info = {
                                    'title': parsed_course['title'],
                                    'platform': parsed_course['platform'],
                                    'duration': parsed_course['duration'],
                                    'url': '',
                                    'reason': item.get('reason', 'N/A')
                                }
                            
                            phase_data['skills'].append({
                                'skill': item.get('skill', f'Skill {j+1}'),
                                'course': course_info,
                                'est_hours': item.get('est_hours', 10)  # Include estimated hours
                            })
                else:
                    # Fallback for unexpected phase type
                    phase_data = {
                        'phase': f'Phase {i+1}',
                        'skills': [{'skill': str(phase), 'course': {'title': 'N/A', 'platform': 'N/A', 'duration': 'N/A', 'url': '', 'reason': 'N/A'}, 'est_hours': 10}],
                        'phase_total_hours': 10,
                        'phase_time_frame': 'Estimated time: 10 hours (~1.25 weeks at 8 hrs/week)'
                    }
                
                roadmap.append(phase_data)
        else:
            print(f"Debug: Unexpected roadmap type, using fallback")
            roadmap = [{
                'phase': 'Phase 1',
                'skills': [{'skill': 'Please try again', 'course': {'title': 'N/A', 'platform': 'N/A', 'duration': 'N/A', 'url': '', 'reason': 'Error processing roadmap'}, 'est_hours': 10}],
                'phase_total_hours': 10,
                'phase_time_frame': 'Estimated time: 10 hours (~1.25 weeks at 8 hrs/week)'
            }]

        # Include performance data in response
        performance_summary = result.get('performance_summary', {})
        time_estimates = result.get('time_estimates', {})
        
        response = {
            'success': True,
            'roadmap': roadmap,
            'resources': 'Personalized course recommendations based on your skill gaps and target role.',
            'time_estimates': {
                'overall_total_hours': time_estimates.get('overall_total_hours', 0),
                'overall_buffered_hours': time_estimates.get('overall_buffered_hours', 0),
                'overall_time_frame': time_estimates.get('overall_time_frame', 'Time estimates not available'),
                'weekly_hours': time_estimates.get('weekly_hours', 8)
            },
            'performance': {
                'generation_time': round(performance_summary.get('total_time', execution_time), 2),
                'cache_hit_ratio': performance_summary.get('cache_stats', {}).get('hit_ratio', 0),
                'step_timings': performance_summary.get('step_timings', {})
            }
        }
        return jsonify(response)
    except Exception as e:
        print(f"Roadmap generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Bind to 0.0.0.0 for containerized development and port forwarding
    app.run(host='0.0.0.0', port=5000, debug=True)


