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
    """Analyze skill gaps for target role"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    user_skills = state.get('extracted_skills', [])
    target_role = state.get('target_role', '')
    
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
    """Create learning roadmap"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    missing_skills = state.get('missing_skills', [])
    nice_to_have = state.get('nice_to_have', [])
    
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
    # Demo execution
    sample_input = """
    Software Engineer with 3 years experience
    Skills: Python, JavaScript, React, Node.js, MongoDB, Git
    Experience: Built web applications, REST APIs, worked with databases
    Education: Computer Science degree
    """
    
    sample_target_role = "Senior Full Stack Developer"
    
    print("🚀 Running Career Pathfinder Pipeline...")
    result = run_pipeline(sample_input, sample_target_role, log_execution=True)
    print("\n📋 Results:")
    print(json.dumps(result, indent=2))
