# 🤖 AI Agents Development
**Assigned to:** M2 - AI Agent Developer  
✅ **COMPLETE** - Multi-agent pipeline with LangGraph

## 🎯 Implemented Features

### � Core AI Pipeline
- **Multi-Agent Architecture**: LangGraph-based workflow with 3 specialized agents
- **Skill Extraction Agent**: Processes resume/CV text and extracts technical skills
- **Gap Analysis Agent**: Compares user skills with target role requirements
- **Roadmap Mentor Agent**: Creates structured 3-phase learning plans with course recommendations

### 🛠️ Technology Stack
- **LangGraph**: Multi-agent workflow orchestration
- **LangChain**: AI agent framework and utilities
- **OpenAI GPT-4o**: Large language model for intelligent analysis
- **Python 3.12+**: Core implementation with TypedDict for type safety

### 📊 Logging & Analytics
- **Comprehensive Logging**: Execution tracking with performance metrics
- **Analytics Dashboard**: Command-line tools for log analysis
- **Performance Monitoring**: Execution time tracking and trends
- **Session Management**: Unique session IDs and historical data

## 📁 Files in this Directory

- `career_pathfinder_langgraph.py` - Main AI pipeline implementation
- `career_logger.py` - Logging system with analytics
- `view_logs.py` - Command-line log viewer and analysis tool
- `requirements.txt` - Python dependencies for AI agents
- `career_pathfinder_logs.json` - Execution logs (auto-generated)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables (in project root)
cp ../.env.example ../.env
# Edit .env with your OpenAI and LangSmith API keys

# Run the AI pipeline
python career_pathfinder_langgraph.py
```

## 💡 Usage Examples

### Basic Pipeline Execution
```python
from career_pathfinder_langgraph import run_pipeline

result = run_pipeline(
    input="Software Engineer with Python, JavaScript, React experience",
    target_role="Senior Full Stack Developer",
    log_execution=True
)

print(f"Extracted Skills: {result['extracted_skills']}")
print(f"Missing Skills: {result['missing_skills']}")
print(f"Roadmap Phases: {len(result['roadmap'])}")
```

### Log Analysis
```bash
# View execution statistics
python view_logs.py --stats

# Filter by target role
python view_logs.py --role "Data Scientist"

# Show full roadmap details
python view_logs.py --full --recent 1
```

## 📈 Integration with Team Data

The AI agents automatically integrate with the team's curated data:
- **Job Roles**: Uses `../data/job_roles.json` for skill requirements
- **Courses**: Leverages `../data/courses.json` for learning recommendations
- **Skills Mapping**: Works with 89 technical skills across 6 career paths

## 🔗 API Integration Points

Ready for backend integration (M1):
```python
# API endpoint handlers can directly use:
from ai_agents.career_pathfinder_langgraph import run_pipeline

@app.route('/api/analyze-skills', methods=['POST'])
def analyze_skills():
    data = request.json
    result = run_pipeline(
        input=data['resume_text'],
        target_role=data['target_role'],
        log_execution=True
    )
    return jsonify(result)
```

## 🎯 Next Steps for Team Integration

1. **Backend (M1)**: Create Flask/FastAPI endpoints using the pipeline
2. **Frontend (M3)**: Design UI components to display roadmaps and analytics
3. **Documentation (M5)**: Include AI agent documentation in user guides
4. **Deployment**: Configure production environment with API keys

---

**Status**: ✅ AI Agents Implementation Complete  
**Ready for**: Team integration and API development
