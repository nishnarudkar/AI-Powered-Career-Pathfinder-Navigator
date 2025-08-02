from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Simulated database for skills and job roles
skills_db = []
job_roles = {
    'data-scientist': ['Python', 'R', 'SQL', 'Machine Learning'],
    'ml-engineer': ['Python', 'TensorFlow', 'PyTorch', 'AWS'],
    'ai-engineer': ['Python', 'Deep Learning', 'NLP', 'TensorFlow'],
    'cloud-architect': ['AWS', 'Azure', 'GCP', 'Kubernetes'],
    'devops-engineer': ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
    'full-stack-developer': ['JavaScript', 'React', 'Node.js', 'SQL'],
    'cybersecurity-analyst': ['Networking', 'Penetration Testing', 'SIEM'],
    'product-manager': ['Agile', 'Scrum', 'Stakeholder Management']
}

# Simulate resume upload and storage
@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    # Simulate saving file (in production, save to cloud storage like S3)
    file.save(os.path.join('uploads', file.filename))
    return jsonify({'success': True})

# Simulate skill extraction from resume
@app.route('/extract-skills', methods=['POST'])
def extract_skills():
    # Placeholder: In production, use NLP (e.g., spacy) to parse resume
    extracted_skills = ['Python', 'SQL']  # Simulated skills
    skills_db.extend(extracted_skills)
    return jsonify({'skills': extracted_skills})

# Generate learning roadmap
@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    skills = data.get('skills', [])
    role = data.get('role', '')
    if not role:
        return jsonify({'error': 'No role selected'})
    
    required_skills = job_roles.get(role, [])
    missing_skills = [skill for skill in required_skills if skill not in skills]
    
    # Simulate roadmap generation
    roadmap = [f'Learn {skill}' for skill in missing_skills]
    resources = 'Recommended: Check Coursera or Udemy for relevant courses.'
    
    return jsonify({'roadmap': roadmap, 'resources': resources})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)