from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
import PyPDF2
from docx import Document
from dotenv import load_dotenv
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
    with open(session_file, 'w') as f:
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
            'assessment_time': round(execution_time, 3)
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Target role readiness assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
                        'skills': [{'skill': phase, 'course': {'title': 'N/A', 'platform': 'N/A', 'url': '', 'reason': 'N/A'}, 'est_hours': 10}],
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
                                course_info = {
                                    'title': course,
                                    'platform': 'N/A',
                                    'url': '',
                                    'reason': item.get('reason', 'N/A')
                                }
                            elif isinstance(course, dict):
                                course_info = {
                                    'title': course.get('title', 'N/A'),
                                    'platform': course.get('platform', 'N/A'),
                                    'url': course.get('url', ''),
                                    'reason': course.get('why', item.get('reason', 'N/A'))
                                }
                            else:
                                course_info = {
                                    'title': str(course) if course else 'N/A',
                                    'platform': 'N/A',
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
                        'skills': [{'skill': str(phase), 'course': {'title': 'N/A', 'platform': 'N/A', 'url': '', 'reason': 'N/A'}, 'est_hours': 10}],
                        'phase_total_hours': 10,
                        'phase_time_frame': 'Estimated time: 10 hours (~1.25 weeks at 8 hrs/week)'
                    }
                
                roadmap.append(phase_data)
        else:
            print(f"Debug: Unexpected roadmap type, using fallback")
            roadmap = [{
                'phase': 'Phase 1',
                'skills': [{'skill': 'Please try again', 'course': {'title': 'N/A', 'platform': 'N/A', 'url': '', 'reason': 'Error processing roadmap'}, 'est_hours': 10}],
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