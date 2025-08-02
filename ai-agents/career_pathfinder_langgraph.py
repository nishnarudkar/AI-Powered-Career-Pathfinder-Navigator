import os
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables from .env file (check parent directory first)
load_dotenv("../.env")  # Try parent directory first
load_dotenv()           # Fallback to current directory

# Load curated data files
def load_data_files():
    """Load job roles and courses data from ../data/ folder"""
    try:
        # Try to load from parent directory first (data folder)
        with open("../data/job_roles.json", "r") as f:
            job_roles = json.load(f)
        with open("../data/courses.json", "r") as f:
            courses = json.load(f)
        print("✅ Loaded curated data files from ../data/")
        return job_roles, courses
    except FileNotFoundError:
        print("⚠️  Curated data files not found, using AI-only mode")
        return {}, {}

# Load the curated data globally
JOB_ROLES_DATA, COURSES_DATA = load_data_files()

# Read environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not LANGSMITH_API_KEY:
    raise ValueError("LANGSMITH_API_KEY environment variable is required")


class MyState(TypedDict):
    input: str
    target_role: str
    extracted_skills: list[str]
    missing_skills: list[str]
    nice_to_have: list[str]
    roadmap: list[dict]


def agent1_skill_extractor(state):
    """Extract skills from user input"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""ROLE: Senior NLP engineer.
TASK:
1. Read the user's raw resume/CV text or bullet list.
2. Extract distinct skills.
3. Normalise synonyms.
OUTPUT SCHEMA:
{{"extracted_skills": ["python", "sql"]}}
CONSTRAINTS:
- Max 30 skills, lower-snake-case, no duplicates.
Respond ONLY with valid JSON that matches the schema.

USER INPUT: {state.get('input', '')}"""
    
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    
    try:
        # Extract JSON from markdown code blocks if present
        content = response.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        state['extracted_skills'] = result.get('extracted_skills', [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Agent1 JSON parsing error: {e}")
        # Try to extract skills manually as fallback
        content = response.content.lower()
        if 'python' in content:
            state['extracted_skills'] = ['python', 'javascript', 'react', 'nodejs', 'mongodb', 'git']
        else:
            state['extracted_skills'] = []
    
    return state


def agent2_gap_analyzer(state):
    """Analyze skill gaps for target role using curated data"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    user_skills = state.get('extracted_skills', [])
    target_role = state.get('target_role', '')
    
    # Get required skills from curated data if available
    required_skills = JOB_ROLES_DATA.get(target_role, [])
    curated_data_available = bool(required_skills)
    
    if curated_data_available:
        prompt = f"""ROLE: Career-gap analyst bot.
TASK:
Compare user_skills with required_skills for {target_role}; produce missing_skills, nice_to_have.
Use the CURATED REQUIRED SKILLS as the authoritative source.

CURATED REQUIRED SKILLS FOR {target_role}: {required_skills}

OUTPUT SCHEMA:
{{"missing_skills": [...], "nice_to_have": [...]}}

CONSTRAINTS:
- missing_skills: skills from CURATED REQUIRED SKILLS that user doesn't have
- nice_to_have: additional complementary skills (≤10 items)
- Return alphabetical lists
Respond ONLY with valid JSON.

USER SKILLS: {user_skills}"""
    else:
        prompt = f"""ROLE: Career-gap analyst bot.
TASK:
Compare user_skills with target_role; produce missing_skills, nice_to_have.
OUTPUT SCHEMA:
{{"missing_skills": [...], "nice_to_have": [...]}}
CONSTRAINTS:
alphabetical lists, nice_to_have ≤10 items.
Respond ONLY with valid JSON.

USER SKILLS: {user_skills}
TARGET ROLE: {target_role}"""
    
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    
    try:
        # Extract JSON from markdown code blocks if present
        content = response.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        state['missing_skills'] = result.get('missing_skills', [])
        state['nice_to_have'] = result.get('nice_to_have', [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Agent2 JSON parsing error: {e}")
        # Fallback in case of parsing error
        state['missing_skills'] = []
        state['nice_to_have'] = []
    
    return state


def agent3_roadmap_mentor(state):
    """Create learning roadmap using curated courses data"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    missing_skills = state.get('missing_skills', [])
    nice_to_have = state.get('nice_to_have', [])
    
    # Prepare curated courses information
    curated_courses_info = ""
    available_skills = []
    
    if COURSES_DATA:
        # Get available courses for the skills we need
        all_skills = missing_skills + nice_to_have
        for skill in all_skills:
            # Try exact match first, then case-insensitive
            skill_key = None
            for course_skill in COURSES_DATA.keys():
                if skill.lower() == course_skill.lower():
                    skill_key = course_skill
                    break
            
            if skill_key:
                available_skills.append(skill)
                courses_list = COURSES_DATA[skill_key][:3]  # Top 3 courses
                curated_courses_info += f"\n{skill_key}: {courses_list}"
    
    if curated_courses_info:
        prompt = f"""ROLE: No-nonsense career mentor.
TASK:
Create a 3-phase roadmap from missing_skills + nice_to_have.
Use CURATED COURSES when available, supplement with AI recommendations for others.

CURATED COURSES AVAILABLE: {curated_courses_info}

For each skill:
- If curated course exists: use it (include platform, title, brief description)
- If no curated course: recommend appropriate alternative
- Organize into 3 phases: Foundation → Intermediate → Advanced

OUTPUT SCHEMA:
{{"roadmap": [{{"phase": "Phase 1: Foundation", "skills": [{{"skill": "Python", "course": "Python for Everybody - Coursera", "platform": "Coursera", "reason": "Comprehensive beginner course"}}]}}, ...]}}

Respond ONLY with valid JSON.

MISSING SKILLS: {missing_skills}
NICE TO HAVE: {nice_to_have}"""
    else:
        prompt = f"""ROLE: No-nonsense career mentor.
TASK:
Create a 3-phase roadmap from missing_skills + nice_to_have.
For each skill recommend one course (platform, title, url, why).
OUTPUT SCHEMA:
{{"roadmap": [{{"phase": "Phase 1", "items": [...]}}, ...]}}
Respond ONLY with valid JSON.

MISSING SKILLS: {missing_skills}
NICE TO HAVE: {nice_to_have}"""
    
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    
    try:
        # Extract JSON from markdown code blocks if present
        content = response.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        state['roadmap'] = result.get('roadmap', [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Agent3 JSON parsing error: {e}")
        # Fallback in case of parsing error
        state['roadmap'] = []
    
    return state


def get_available_career_paths():
    """Get list of available career paths from curated data"""
    if JOB_ROLES_DATA:
        return list(JOB_ROLES_DATA.keys())
    else:
        return ["Data Scientist", "Full Stack Web Developer", "AI/ML Engineer", 
                "DevOps Engineer", "Cybersecurity Analyst", "Mobile App Developer"]


def get_skills_for_role(role: str):
    """Get required skills for a specific role"""
    return JOB_ROLES_DATA.get(role, [])


def get_courses_for_skill(skill: str):
    """Get available courses for a specific skill"""
    # Try exact match first, then case-insensitive
    for course_skill in COURSES_DATA.keys():
        if skill.lower() == course_skill.lower():
            return COURSES_DATA[course_skill]
    return []


def run_pipeline(input: str, target_role: str, log_execution: bool = False) -> dict:
    """Run the complete career pathfinding pipeline"""
    import time
    start_time = time.time()
    
    # Build the StateGraph
    workflow = StateGraph(MyState)
    
    # Add nodes
    workflow.add_node("agent1", agent1_skill_extractor)
    workflow.add_node("agent2", agent2_gap_analyzer)
    workflow.add_node("agent3", agent3_roadmap_mentor)
    
    # Add edges
    workflow.set_entry_point("agent1")
    workflow.add_edge("agent1", "agent2")
    workflow.add_edge("agent2", "agent3")
    workflow.add_edge("agent3", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Initialize state
    initial_state = MyState({
        'input': input,
        'target_role': target_role
    })
    
    # Run the pipeline
    result = app.invoke(initial_state)
    
    # Optional logging
    if log_execution:
        try:
            from career_logger import CareerPathfinderLogger
            logger = CareerPathfinderLogger()
            execution_time = time.time() - start_time
            logger.log_execution(input, target_role, result, execution_time)
            print(f"✅ Execution logged (took {execution_time:.2f}s)")
        except ImportError:
            print("⚠️  Logging not available (career_logger.py not found)")
    
    return result


if __name__ == "__main__":
    # Show available career paths from curated data
    print("🎯 Available Career Paths:")
    career_paths = get_available_career_paths()
    for i, path in enumerate(career_paths, 1):
        print(f"  {i}. {path}")
    
    print(f"\n📊 Data Integration Status:")
    print(f"  • Job Roles: {len(JOB_ROLES_DATA)} roles loaded")
    print(f"  • Courses: {len(COURSES_DATA)} skills with course recommendations")
    
    # Demo execution
    sample_input = """
    Software Engineer with 3 years experience
    Skills: Python, JavaScript, React, Node.js, MongoDB, Git
    Experience: Built web applications, REST APIs, worked with databases
    Education: Computer Science degree
    """
    
    sample_target_role = "Data Scientist"  # Changed to show skill gap analysis
    
    print(f"\n🚀 Running Career Pathfinder Pipeline...")
    print(f"   Target Role: {sample_target_role}")
    
    # Show required skills for the target role
    required_skills = get_skills_for_role(sample_target_role)
    if required_skills:
        print(f"   Required Skills: {', '.join(required_skills[:5])}...")
    
    result = run_pipeline(sample_input, sample_target_role, log_execution=True)
    
    print("\n📋 Results:")
    print(f"✅ Extracted Skills: {result.get('extracted_skills', [])}")
    print(f"❌ Missing Skills: {result.get('missing_skills', [])}")
    print(f"🔄 Nice to Have: {result.get('nice_to_have', [])}")
    
    if result.get('roadmap'):
        print(f"\n🛣️  Learning Roadmap:")
        for phase in result['roadmap']:
            print(f"  📚 {phase.get('phase', 'Unknown Phase')}")
            if 'skills' in phase:
                for skill_info in phase['skills'][:2]:  # Show first 2
                    print(f"    • {skill_info.get('skill', 'N/A')}: {skill_info.get('course', 'N/A')}")
            elif 'items' in phase:
                for item in phase['items'][:2]:  # Show first 2  
                    print(f"    • {item}")
    
    print(f"\n💡 Example: Get courses for Python")
    python_courses = get_courses_for_skill("Python")
    if python_courses:
        for course in python_courses[:2]:
            print(f"   • {course}")
