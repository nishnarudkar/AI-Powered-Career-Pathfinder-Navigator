import os
import json
import time
import hashlib
import threading
from typing import TypedDict, Dict, List, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../.env")
load_dotenv()

# Performance monitoring
class PerformanceProfiler:
    def __init__(self):
        self.timings = {}
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def start_timer(self, step_name: str):
        self.timings[step_name] = {'start': time.time()}
        
    def end_timer(self, step_name: str):
        if step_name in self.timings:
            self.timings[step_name]['end'] = time.time()
            self.timings[step_name]['duration'] = self.timings[step_name]['end'] - self.timings[step_name]['start']
            
    def get_performance_report(self) -> dict:
        report = {
            'step_timings': {},
            'total_time': 0,
            'cache_stats': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_ratio': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
            }
        }
        
        total_time = 0
        for step, timing in self.timings.items():
            if 'duration' in timing:
                report['step_timings'][step] = round(timing['duration'], 3)
                total_time += timing['duration']
                
        report['total_time'] = round(total_time, 3)
        return report
        
    def cache_get(self, key: str):
        if key in self.cache:
            self.cache_hits += 1
            return self.cache[key]
        self.cache_misses += 1
        return None
        
    def cache_set(self, key: str, value):
        self.cache[key] = value

# Global profiler instance
profiler = PerformanceProfiler()

# Load curated data files with caching
def load_data_files():
    """Load job roles and courses data from ../data/ folder with caching"""
    import os
    
    # Try different possible paths
    possible_paths = [
        "../data/",
        "./data/",
        "data/",
        "/workspaces/AI-Powered-Career-Pathfinder-Navigator/data/"
    ]
    
    for base_path in possible_paths:
        try:
            job_roles_path = os.path.join(base_path, "job_roles.json")
            courses_path = os.path.join(base_path, "courses.json")
            
            if os.path.exists(job_roles_path) and os.path.exists(courses_path):
                with open(job_roles_path, "r", encoding='utf-8') as f:
                    job_roles = json.load(f)
                with open(courses_path, "r", encoding='utf-8') as f:
                    courses = json.load(f)
                print(f"✅ Loaded curated data files from {base_path}")
                return (job_roles, courses)
        except Exception as e:
            continue
    
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

# Performance configuration
PERFORMANCE_CONFIG = {
    'max_gaps_to_process': 8,  # Restored to original
    'max_courses_per_skill': 6,  # Restored to original
    'max_generation_time': 30.0,  # Increased for slower, more thorough processing
    'llm_timeout': 30.0,  # Allow plenty of time for LLM calls
    'enable_parallel_processing': False,  # Disabled for simplicity
    'enable_caching': False,  # Disabled to avoid caching issues
    'max_cache_entries': 100
}

# Time estimation configuration
TIME_ESTIMATION_CONFIG = {
    'default_weekly_hours': 8,  # Default weekly study capacity
    'buffer_percentage': 10,  # 10% buffer for friction and overlap
    'parallel_efficiency': 0.85,  # 15% time reduction when tasks can be done in parallel
}

class MyState(TypedDict, total=False):
    input: str
    target_role: str
    extracted_skills: list[str]
    missing_skills: list[str]
    nice_to_have: list[str]
    roadmap: list[dict]
    time_estimates: dict
    performance_data: dict

def get_priority_skills(missing_skills: list, nice_to_have: list, max_count: int = 8) -> Tuple[List[str], List[str]]:
    """Trim input to top priority skills"""
    profiler.start_timer('input_trimming')
    
    # Prioritize missing_skills over nice_to_have
    total_skills = len(missing_skills) + len(nice_to_have)
    
    if total_skills <= max_count:
        result = (missing_skills, nice_to_have)
    else:
        # Allocate at least 60% to missing skills
        missing_quota = min(len(missing_skills), max(int(max_count * 0.6), max_count - len(nice_to_have)))
        nice_quota = max_count - missing_quota
        
        result = (missing_skills[:missing_quota], nice_to_have[:nice_quota])
    
    profiler.end_timer('input_trimming')
    return result

def get_course_candidates_parallel(skills: List[str]) -> Dict[str, List[str]]:
    """Retrieve course candidates for skills in parallel"""
    profiler.start_timer('course_retrieval')
    
    def get_courses_for_skill_optimized(skill: str) -> Tuple[str, List[str]]:
        """Get optimized course list for a single skill"""
        # Try exact match first, then case-insensitive
        for course_skill in COURSES_DATA.keys():
            if skill.lower() == course_skill.lower():
                courses = COURSES_DATA[course_skill][:PERFORMANCE_CONFIG['max_courses_per_skill']]
                # Return compact summaries instead of full descriptions
                compact_courses = []
                for course in courses:
                    # Extract just title and platform
                    if ' - ' in course:
                        title_platform = course.split(' (')[0]  # Remove additional info in parentheses
                        compact_courses.append(title_platform)
                    else:
                        compact_courses.append(course)
                return skill, compact_courses
        return skill, []
    
    course_candidates = {}
    
    if PERFORMANCE_CONFIG['enable_parallel_processing']:
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_skill = {executor.submit(get_courses_for_skill_optimized, skill): skill for skill in skills}
            for future in as_completed(future_to_skill):
                skill, courses = future.result()
                if courses:
                    course_candidates[skill] = courses
    else:
        for skill in skills:
            skill, courses = get_courses_for_skill_optimized(skill)
            if courses:
                course_candidates[skill] = courses
    
    profiler.end_timer('course_retrieval')
    return course_candidates

def agent3_roadmap_mentor_optimized(state):
    """Optimized learning roadmap generation with performance profiling"""
    profiler.start_timer('roadmap_generation_total')
    
    missing_skills = state.get('missing_skills', [])
    nice_to_have = state.get('nice_to_have', [])
    target_role = state.get('target_role', '')
    
    print(f"🔄 Generating new roadmap")
    
    # Step 1: Input trimming
    priority_missing, priority_nice = get_priority_skills(
        missing_skills, nice_to_have, PERFORMANCE_CONFIG['max_gaps_to_process']
    )
    
    all_priority_skills = priority_missing + priority_nice
    print(f"📊 Processing {len(all_priority_skills)} priority skills out of {len(missing_skills + nice_to_have)} total")
    
    # Step 2: Parallel course retrieval
    course_candidates = get_course_candidates_parallel(all_priority_skills)
    
    # Step 3: Prepare compact course information for LLM
    profiler.start_timer('llm_prompt_preparation')
    
    curated_courses_info = ""
    if course_candidates:
        for skill, courses in course_candidates.items():
            course_list = ", ".join(courses[:3])  # Max 3 courses per skill
            curated_courses_info += f"{skill}: {course_list}\\n"
    
    # Step 4: Enhanced LLM prompt to request time estimates
    if curated_courses_info:
        prompt = f"""Create JSON roadmap using these courses:
{curated_courses_info}

Build a 3-phase plan (Foundation, Applied, Capstone) with 9-12 steps total. Each step includes skill, course, reason, and est_hours (estimated learning hours).

Required JSON format:
{{"roadmap": [{{"phase": "Phase 1: Foundation", "skills": [{{"skill": "Python", "course": "Python for Everybody - Coursera", "reason": "Good for beginners", "est_hours": 15}}]}}]}}

MISSING: {priority_missing}
NICE: {priority_nice}

Guidelines for est_hours:
- Basic tools (Git, Excel): 6-8 hours
- Web technologies (HTML, CSS): 8-10 hours  
- Cloud platforms: 10-12 hours
- Databases: 12-15 hours
- Programming languages/frameworks: 15-20 hours
- Data science/ML: 18-25 hours

Return only valid JSON, max 10 words per reason."""
    else:
        prompt = f"""Create JSON roadmap for skills transition.

Build a 3-phase plan (Foundation, Applied, Capstone) with 9-12 steps total. Each step includes skill, course, reason, and est_hours (estimated learning hours).

Required JSON format:
{{"roadmap": [{{"phase": "Phase 1", "skills": [{{"skill": "X", "course": "Course - Platform", "reason": "Brief reason", "est_hours": 15}}]}}]}}

MISSING: {priority_missing}
NICE: {priority_nice}

Guidelines for est_hours:
- Basic tools: 6-8 hours
- Web technologies: 8-10 hours  
- Cloud platforms: 10-12 hours
- Databases: 12-15 hours
- Programming languages: 15-20 hours
- Data science/ML: 18-25 hours

Return only valid JSON, max 10 words per reason."""
    
    profiler.end_timer('llm_prompt_preparation')
    
    # Step 5: LLM call with aggressive timeout protection
    profiler.start_timer('llm_call')
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, timeout=PERFORMANCE_CONFIG['llm_timeout'])  # Use full gpt-4o model
        message = HumanMessage(content=prompt)
        
        response = llm.invoke([message])
        # Handle response content properly
        content = response.content if isinstance(response.content, str) else str(response.content)
        roadmap_result = parse_llm_response(content)
        
        # If parsing failed, use fallback
        if not roadmap_result:
            print("⚠️ LLM response parsing failed, using fallback")
            roadmap_result = generate_fallback_roadmap(priority_missing, priority_nice)
            
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        roadmap_result = generate_fallback_roadmap(priority_missing, priority_nice)
    
    profiler.end_timer('llm_call')
    
    # Step 6: Post-processing with time estimates
    profiler.start_timer('post_processing')
    
    # Apply time estimation to the roadmap
    enhanced_roadmap_data = calculate_time_estimates(roadmap_result)
    
    # Update state with enhanced roadmap structure
    state['roadmap'] = enhanced_roadmap_data['phases']
    state['time_estimates'] = {
        'overall_total_hours': enhanced_roadmap_data['overall_total_hours'],
        'overall_buffered_hours': enhanced_roadmap_data['overall_buffered_hours'],
        'overall_time_frame': enhanced_roadmap_data['overall_time_frame'],
        'weekly_hours': enhanced_roadmap_data['weekly_hours']
    }
    
    # Cache the result (disabled for simplicity)
    # if PERFORMANCE_CONFIG['enable_caching']:
    #     profiler.cache_set(cache_key, roadmap_result)
    
    profiler.end_timer('post_processing')
    profiler.end_timer('roadmap_generation_total')
    
    # Add performance data to state
    state['performance_data'] = profiler.get_performance_report()
    
    # Log performance summary with time estimates
    perf_data = state['performance_data']
    time_est = state.get('time_estimates', {})
    print(f"⚡ Roadmap generated in {perf_data['total_time']}s (cache hit ratio: {perf_data['cache_stats']['hit_ratio']:.1%})")
    print(f"📚 Learning plan: {time_est.get('overall_time_frame', 'Time estimates not available')}")
    
    # Warning if exceeding budget
    if perf_data['total_time'] > PERFORMANCE_CONFIG['max_generation_time']:
        print(f"⚠️ Generation time ({perf_data['total_time']}s) exceeded budget ({PERFORMANCE_CONFIG['max_generation_time']}s)")
    
    return state

def parse_llm_response(content: str) -> List[dict]:
    """Parse LLM response with error handling"""
    try:
        # Extract JSON from markdown code blocks if present
        content = content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        return result.get('roadmap', [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"JSON parsing error: {e}")
        return []

def calculate_time_estimates(roadmap: List[dict], weekly_hours: Optional[int] = None) -> dict:
    """Calculate time estimates for phases and overall roadmap"""
    import math
    
    if weekly_hours is None:
        weekly_hours = TIME_ESTIMATION_CONFIG['default_weekly_hours']
    
    # Ensure weekly_hours is positive integer
    weekly_hours = max(1, weekly_hours) if isinstance(weekly_hours, int) else TIME_ESTIMATION_CONFIG['default_weekly_hours']
    
    buffer_percentage = TIME_ESTIMATION_CONFIG['buffer_percentage']
    parallel_efficiency = TIME_ESTIMATION_CONFIG['parallel_efficiency']
    
    enhanced_roadmap = []
    overall_total_hours = 0
    
    for phase in roadmap:
        if not isinstance(phase, dict):
            continue
            
        phase_copy = phase.copy()
        phase_skills = phase_copy.get('skills', [])
        phase_total_hours = 0
        
        # Ensure each skill has est_hours
        for skill in phase_skills:
            if isinstance(skill, dict):
                if 'est_hours' not in skill:
                    # Assign default estimated hours based on skill complexity
                    skill['est_hours'] = estimate_skill_hours(skill.get('skill', ''))
                phase_total_hours += skill.get('est_hours', 0)
        
        # Calculate phase time frame
        phase_weeks = math.ceil(phase_total_hours / weekly_hours)
        phase_time_frame = f"Estimated time: {phase_total_hours} hours (~{phase_weeks} week{'s' if phase_weeks != 1 else ''} at {weekly_hours} hrs/week)"
        
        # Add parallel efficiency note if applicable
        if len(phase_skills) > 2:
            effective_hours = int(phase_total_hours * parallel_efficiency)
            effective_weeks = math.ceil(effective_hours / weekly_hours)
            phase_time_frame += f". Some foundational steps can overlap; effective calendar time may be {effective_hours}h (~{effective_weeks} week{'s' if effective_weeks != 1 else ''})"
        
        phase_copy['phase_total_hours'] = phase_total_hours
        phase_copy['phase_time_frame'] = phase_time_frame
        
        enhanced_roadmap.append(phase_copy)
        overall_total_hours += phase_total_hours
    
    # Calculate overall time estimates with buffer
    buffered_hours = int(overall_total_hours * (1 + buffer_percentage / 100))
    overall_weeks = math.ceil(overall_total_hours / weekly_hours)
    buffered_weeks = math.ceil(buffered_hours / weekly_hours)
    
    overall_time_frame = f"Total: {overall_total_hours}h (+{buffer_percentage}% buffer {buffered_hours}h) ≈ {buffered_weeks} weeks at {weekly_hours}h/week"
    
    return {
        'phases': enhanced_roadmap,
        'overall_total_hours': overall_total_hours,
        'overall_buffered_hours': buffered_hours,
        'overall_time_frame': overall_time_frame,
        'weekly_hours': weekly_hours
    }

def estimate_skill_hours(skill: str) -> int:
    """Estimate learning hours for a skill based on complexity"""
    skill_lower = skill.lower()
    
    # Programming languages and frameworks (higher complexity)
    if any(lang in skill_lower for lang in ['python', 'javascript', 'java', 'react', 'angular', 'vue', 'django', 'flask', 'nodejs']):
        return 15
    
    # Database and infrastructure (medium-high complexity)
    elif any(db in skill_lower for db in ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes']):
        return 12
    
    # Cloud platforms (medium complexity)
    elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'cloud']):
        return 10
    
    # Data science and ML (high complexity)
    elif any(ds in skill_lower for ds in ['machine-learning', 'data-science', 'tensorflow', 'pytorch', 'pandas', 'numpy']):
        return 18
    
    # Tools and utilities (lower complexity)
    elif any(tool in skill_lower for tool in ['git', 'jira', 'figma', 'excel', 'tableau']):
        return 6
    
    # Web technologies (medium complexity)
    elif any(web in skill_lower for web in ['html', 'css', 'bootstrap', 'sass', 'tailwind']):
        return 8
    
    # Default for unrecognized skills
    else:
        return 10

def generate_fallback_roadmap(missing_skills: List[str], nice_to_have: List[str]) -> List[dict]:
    """Generate a basic roadmap when LLM fails or times out"""
    all_skills = missing_skills + nice_to_have
    
    if not all_skills:
        return []
    
    # Simple 3-phase distribution
    skills_per_phase = max(1, len(all_skills) // 3)
    
    roadmap = []
    phases = ["Phase 1: Foundation", "Phase 2: Intermediate", "Phase 3: Advanced"]
    
    for i, phase in enumerate(phases):
        start_idx = i * skills_per_phase
        end_idx = start_idx + skills_per_phase if i < 2 else len(all_skills)
        phase_skills = all_skills[start_idx:end_idx]
        
        if phase_skills:
            skills_data = []
            for skill in phase_skills:
                # Get course from curated data if available
                skill_name, course_list = get_courses_for_skill_optimized(skill)
                course_title = course_list[0] if course_list else f"Learn {skill} - Online Course"
                
                skills_data.append({
                    "skill": skill,
                    "course": course_title,
                    "reason": f"Essential {skill} skills",
                    "est_hours": estimate_skill_hours(skill)
                })
            
            roadmap.append({
                "phase": phase,
                "skills": skills_data
            })
    
    return roadmap

def get_courses_for_skill_optimized(skill: str) -> Tuple[str, List[str]]:
    """Optimized course retrieval for single skill"""
    for course_skill in COURSES_DATA.keys():
        if skill.lower() == course_skill.lower():
            return skill, COURSES_DATA[course_skill][:3]
    return skill, []

def agent1_skill_extractor(state):
    """Extract skills from user input with enhanced fallback mechanism"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""ROLE: Senior NLP engineer specializing in resume/CV skill extraction.
TASK:
1. Read the user's raw resume/CV text, project descriptions, or bullet list.
2. Extract distinct technical skills, tools, frameworks, and technologies.
3. Normalize synonyms (e.g., "React.js" → "react", "Node.js" → "nodejs").
4. Focus on technical skills relevant for software development careers.

OUTPUT SCHEMA:
{{"extracted_skills": ["python", "sql", "react", "git"]}}

CONSTRAINTS:
- Max 30 skills, lowercase, hyphenated format, no duplicates
- Include programming languages, frameworks, databases, tools, platforms
- Exclude soft skills, job titles, company names
- Normalize common variations (JavaScript/JS → "javascript", PostgreSQL/Postgres → "postgresql")

Respond ONLY with valid JSON that matches the schema.

USER INPUT: {state.get('input', '')}"""
    
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    
    try:
        # Extract JSON from markdown code blocks if present
        content = response.content if isinstance(response.content, str) else str(response.content)
        content = content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        extracted_skills = result.get('extracted_skills', [])
        
        # Validate and clean the extracted skills
        cleaned_skills = []
        for skill in extracted_skills:
            if isinstance(skill, str) and len(skill.strip()) > 0:
                # Normalize skill format
                normalized_skill = skill.strip().lower().replace(' ', '-')
                if normalized_skill not in cleaned_skills:
                    cleaned_skills.append(normalized_skill)
        
        state['extracted_skills'] = cleaned_skills[:30]  # Limit to 30 skills
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Agent1 JSON parsing error: {e}")
        print(f"Response content: {response.content[:200] if isinstance(response.content, str) else str(response.content)[:200]}...")
        
        # Enhanced fallback mechanism using pattern matching
        fallback_skills = extract_skills_fallback(state.get('input', ''))
        state['extracted_skills'] = fallback_skills
        print(f"Using fallback extraction: {len(fallback_skills)} skills found")
    
    return state

def extract_skills_fallback(text: str) -> list[str]:
    """Enhanced fallback skill extraction using pattern matching"""
    import re
    
    # Comprehensive skill dictionary with common variations
    skill_patterns = {
        'python': r'\b(python|py)\b',
        'javascript': r'\b(javascript|js|java-script)\b',
        'java': r'\b(java)\b(?!script)',  # Java but not JavaScript
        'csharp': r'\b(c#|csharp|c-sharp)\b',
        'cpp': r'\b(c\+\+|cpp|c plus plus)\b',
        'typescript': r'\b(typescript|ts)\b',
        'react': r'\b(react|react\.js|reactjs)\b',
        'nodejs': r'\b(node\.js|nodejs|node js)\b',
        'vuejs': r'\b(vue\.js|vue|vuejs)\b',
        'angular': r'\b(angular|angularjs)\b',
        'django': r'\b(django)\b',
        'flask': r'\b(flask)\b',
        'express': r'\b(express|express\.js|expressjs)\b',
        'mongodb': r'\b(mongodb|mongo)\b',
        'postgresql': r'\b(postgresql|postgres)\b',
        'mysql': r'\b(mysql)\b',
        'sqlite': r'\b(sqlite)\b',
        'redis': r'\b(redis)\b',
        'git': r'\b(git)\b',
        'docker': r'\b(docker)\b',
        'kubernetes': r'\b(kubernetes|k8s)\b',
        'aws': r'\b(aws|amazon web services)\b',
        'azure': r'\b(azure|microsoft azure)\b',
        'gcp': r'\b(gcp|google cloud|google cloud platform)\b',
        'html': r'\b(html|html5)\b',
        'css': r'\b(css|css3)\b',
        'bootstrap': r'\b(bootstrap)\b',
        'tailwind': r'\b(tailwind|tailwindcss)\b',
        'sass': r'\b(sass|scss)\b',
        'sql': r'\b(sql)\b',
        'nosql': r'\b(nosql)\b',
        'rest-api': r'\b(rest|rest api|rest apis|restful)\b',
        'graphql': r'\b(graphql)\b',
        'json': r'\b(json)\b',
        'xml': r'\b(xml)\b',
        'pandas': r'\b(pandas)\b',
        'numpy': r'\b(numpy)\b',
        'scikit-learn': r'\b(scikit-learn|sklearn)\b',
        'tensorflow': r'\b(tensorflow)\b',
        'pytorch': r'\b(pytorch)\b',
        'machine-learning': r'\b(machine learning|ml|machine-learning)\b',
        'data-science': r'\b(data science|data-science)\b',
        'deep-learning': r'\b(deep learning|deep-learning)\b',
        'tableau': r'\b(tableau)\b',
        'powerbi': r'\b(power bi|powerbi|power-bi)\b',
        'excel': r'\b(excel|microsoft excel)\b',
        'jupyter': r'\b(jupyter|jupyter notebook|jupyter notebooks)\b',
        'linux': r'\b(linux|ubuntu|centos)\b',
        'windows': r'\b(windows)\b',
        'macos': r'\b(macos|mac os)\b',
        'bash': r'\b(bash|shell scripting)\b',
        'powershell': r'\b(powershell)\b',
        'jira': r'\b(jira)\b',
        'confluence': r'\b(confluence)\b',
        'slack': r'\b(slack)\b',
        'figma': r'\b(figma)\b',
        'photoshop': r'\b(photoshop|adobe photoshop)\b'
    }
    
    text_lower = text.lower()
    extracted_skills = []
    
    # Use regex patterns to find skills
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, text_lower):
            if skill not in extracted_skills:
                extracted_skills.append(skill)
    
    # Additional pattern for programming languages mentioned in context
    prog_lang_pattern = r'\b(programming languages?|languages?|coded?\s+in|built\s+with|using|experience\s+with)\s*:?\s*([a-zA-Z+#.,\s]+)'
    matches = re.findall(prog_lang_pattern, text_lower)
    for match in matches:
        lang_text = match[1]
        for skill, pattern in skill_patterns.items():
            if re.search(pattern, lang_text):
                if skill not in extracted_skills:
                    extracted_skills.append(skill)
    
    return extracted_skills[:30]  # Limit to 30 skills

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
        content = response.content if isinstance(response.content, str) else str(response.content)
        content = content.strip()
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
    """Get available courses for a specific skill (legacy function)"""
    _, courses = get_courses_for_skill_optimized(skill)
    return courses

def extract_skills_only(input_text: str) -> dict:
    """Fast skill extraction without full pipeline"""
    print(f"🔍 Extracting skills only from input")
    
    # Initialize profiler for timing
    global profiler
    profiler = PerformanceProfiler()
    profiler.start_timer('skill_extraction_only')
    
    # Create a minimal state for skill extraction
    state = {'input': input_text}
    
    # Run only the skill extraction agent
    try:
        result_state = agent1_skill_extractor(state)
        extracted_skills = result_state.get('extracted_skills', [])
        
        profiler.end_timer('skill_extraction_only')
        performance_data = profiler.get_performance_report()
        
        print(f"⚡ Skills extracted in {performance_data['total_time']}s")
        
        return {
            'extracted_skills': extracted_skills,
            'performance_summary': performance_data
        }
    except Exception as e:
        print(f"❌ Skill extraction failed: {e}")
        # Fallback to pattern matching
        fallback_skills = extract_skills_fallback(input_text)
        return {
            'extracted_skills': fallback_skills,
            'performance_summary': {'total_time': 0, 'cache_stats': {'hit_ratio': 0}}
        }

def run_pipeline_optimized(input_text: str, target_role: str, log_execution: bool = False) -> dict:
    """Run optimized career pathfinding pipeline with performance monitoring"""
    
    # Reset profiler for new run
    global profiler
    profiler = PerformanceProfiler()
    
    profiler.start_timer('pipeline_total')
    
    print(f"🚀 Starting optimized pipeline for role: {target_role}")
    
    # Build the StateGraph (using optimized agent3)
    workflow = StateGraph(MyState)
    
    # Add nodes (agent3 is now optimized)
    workflow.add_node("agent1", agent1_skill_extractor)
    workflow.add_node("agent2", agent2_gap_analyzer)
    workflow.add_node("agent3", agent3_roadmap_mentor_optimized)
    
    # Add edges
    workflow.set_entry_point("agent1")
    workflow.add_edge("agent1", "agent2")
    workflow.add_edge("agent2", "agent3")
    workflow.add_edge("agent3", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Initialize state
    initial_state = MyState({
        'input': input_text,
        'target_role': target_role
    })
    
    # Run the pipeline
    result = app.invoke(initial_state)
    
    profiler.end_timer('pipeline_total')
    
    # Add final performance summary
    performance_summary = profiler.get_performance_report()
    result['performance_summary'] = performance_summary
    
    if log_execution:
        print(f"📊 Pipeline Performance Summary:")
        print(f"   Total time: {performance_summary['total_time']}s")
        print(f"   Cache hit ratio: {performance_summary['cache_stats']['hit_ratio']:.1%}")
        for step, duration in performance_summary['step_timings'].items():
            print(f"   {step}: {duration}s")
    
    return result

# Wrapper for backwards compatibility
def run_pipeline(input_text: str, target_role: str, log_execution: bool = False) -> dict:
    """Backwards compatible wrapper for optimized pipeline"""
    return run_pipeline_optimized(input_text, target_role, log_execution)

if __name__ == "__main__":
    # Performance comparison test
    print("🧪 Running performance comparison test...")
    
    sample_input = """
    Software Engineer with 3 years experience
    Skills: Python, JavaScript, React, Node.js, MongoDB, Git
    Experience: Built web applications, REST APIs, worked with databases
    Education: Computer Science degree
    """
    
    sample_target_role = "Data Scientist"
    
    # Test optimized version
    print("\\n🚀 Testing optimized pipeline...")
    start_time = time.time()
    result_optimized = run_pipeline_optimized(sample_input, sample_target_role, log_execution=True)
    optimized_time = time.time() - start_time
    
    print(f"\\n📈 Performance Results:")
    print(f"   Pipeline execution: {optimized_time:.2f}s")
    print(f"   Roadmap phases: {len(result_optimized.get('roadmap', []))}")
    
    # Test second run
    print("\\n🔄 Testing second run...")
    start_time = time.time()
    result_second = run_pipeline_optimized(sample_input, sample_target_role, log_execution=True)
    second_time = time.time() - start_time
    
    print(f"   Second run: {second_time:.2f}s")
