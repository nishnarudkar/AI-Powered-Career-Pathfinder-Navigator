# 🚀 AI-Powered Career Pathfinder Navigator

## � Project Overview
An intelligent career guidance platform that analyzes skill gaps and recommends personalized learning paths using AI agents. Built with a multi-agent LangGraph pipeline powered by OpenAI GPT-4o.

## ✨ Features
- 🔍 **Skill Gap Analysis**: Compare your skills with job requirements using AI
- 🎯 **Personalized Learning Paths**: AI-curated course recommendations with 3-phase roadmaps
- 📊 **Career Roadmaps**: Visual progression paths for 6+ tech careers
- 🤖 **Resume Parsing**: Automatic skill extraction from resumes/CVs
- 📈 **Progress Tracking**: Comprehensive logging and analytics system
- 🛠️ **Multi-Agent Pipeline**: LangGraph-based workflow with skill extraction, gap analysis, and roadmap creation

## 🚀 Quick Demo

```python
from ai_agents.career_pathfinder_langgraph import run_pipeline
out = run_pipeline(
    input="Experienced in python and sql, built dashboards.",
    target_role="Data Scientist"
)
print(out["roadmap"][0])
```

## 🛠️ Tech Stack
- **Backend**: Python 3.12+, Flask/FastAPI
- **Frontend**: React, Tailwind CSS
- **AI/ML**: OpenAI GPT-4o, LangGraph, LangChain
- **Database**: MongoDB/PostgreSQL
- **Data**: JSON-based skill and course mappings
- **Logging**: Comprehensive execution tracking and analytics

## 👥 Team Structure
| Role | Member | Folder | Responsibilities |
|------|--------|--------|------------------|
| **M1** | Backend Lead | `/backend` | API development, database, server setup |
| **M2** | AI Agent Developer | `/ai-agents` | Gap analysis, learning path, NLP agents ✅ |
| **M3** | Frontend Developer | `/frontend` | React UI, user experience, dashboard |
| **M4** | Data Curator | `/data` | Job roles, skills mapping, course curation ✅ |
| **M5** | Documentation | `/docs` | Technical docs, user guides, presentations ✅ |

## 🎯 Supported Career Paths
- 📊 **Data Scientist** (14 skills mapped)
- 💻 **Full Stack Web Developer** (15 skills mapped) ✅ Implemented
- 🤖 **AI/ML Engineer** (15 skills mapped)
- ⚙️ **DevOps Engineer** (15 skills mapped)
- 🔒 **Cybersecurity Analyst** (15 skills mapped)
- 📱 **Mobile App Developer** (15 skills mapped)

## 📊 Dataset Overview
- **89 Technical Skills** mapped across 6 career paths
- **200+ Learning Resources** from IBM SkillsBuild, Coursera, YouTube
- **70% Free Resources** ensuring accessibility
- **JSON-based structure** optimized for AI agent integration

## 🚀 Installation & Setup

### Prerequisites
```bash
- Python 3.12+
- OpenAI API Key
- LangSmith API Key (optional)
- Node.js 16+ (for frontend)
```

### AI Agents Setup (Currently Implemented)
```bash
# Clone repository
git clone https://github.com/nishnarudkar/AI-Powered-Career-Pathfinder-Navigator.git
cd AI-Powered-Career-Pathfinder-Navigator

# Install AI agent dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the AI pipeline
cd ai-agents
python career_pathfinder_langgraph.py
```

### Full Stack Setup (Coming Soon)
```bash
# Backend setup (M1's work)
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup (M3's work)  
cd frontend
npm install
npm start
```

## 🔧 API Endpoints
```
POST /api/analyze-skills    # Skill gap analysis ✅ Implemented
POST /api/learning-path     # Get personalized recommendations ✅ Implemented
POST /api/upload-resume     # Resume parsing and skill extraction ✅ Implemented
GET  /api/career-paths      # Available career paths
GET  /api/courses          # Course recommendations by skill
```

## 📁 Project Structure
```
AI-Powered-Career-Pathfinder-Navigator/
├── ai-agents/                       # ✅ M2 - AI agents implementation
│   ├── career_pathfinder_langgraph.py    # Main AI pipeline
│   ├── career_logger.py                  # Logging system
│   ├── view_logs.py                      # Log viewer utility
│   ├── requirements.txt                  # AI agent dependencies
│   └── career_pathfinder_logs.json       # Execution logs
├── data/                            # ✅ Skills & courses dataset
├── backend/                         # 🔄 M1 - API development
├── frontend/                        # 🔄 M3 - React UI development  
├── docs/                           # ✅ M5 - Documentation
├── deployment/                     # ⏳ Team - Deployment config
├── documentation.md                # ✅ Technical documentation
└── SECURITY.md                     # ✅ Security guidelines
```

## 🤖 AI Agent Architecture

The system uses a multi-agent pipeline built with LangGraph:

```
Input → Agent1 (Skill Extract) → Agent2 (Gap Analysis) → Agent3 (Roadmap) → Output
```

### Agent Functions
- **Agent 1**: Extracts technical skills from resume/CV text
- **Agent 2**: Compares user skills with target role requirements
- **Agent 3**: Creates structured 3-phase learning roadmap with course recommendations

## 📊 Logging & Analytics

```bash
# View execution logs
cd ai-agents
python view_logs.py --stats

# Filter by target role
python view_logs.py --role "Data Scientist"

# Full roadmap details
python view_logs.py --full
```

## 🤝 Contributing
1. Accept collaboration invitation (check email)
2. Clone repository: `git clone [repo-url]`
3. Create feature branch: `git checkout -b feature/your-feature`
4. Work in your assigned folder
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/your-feature`
7. Create Pull Request for review

## 📚 Data Integration

### AI Agent Usage (M2) ✅ Implemented
```python
# Complete pipeline execution
result = run_pipeline(
    input="Software Engineer with Python experience",
    target_role="Senior Full Stack Developer",
    log_execution=True
)

# Access results
extracted_skills = result["extracted_skills"]
missing_skills = result["missing_skills"]
roadmap = result["roadmap"]
```

### Backend Integration (M1)
```python
import json
with open('data/job_roles.json') as f:
    job_roles = json.load(f)
with open('data/courses.json') as f:
    courses = json.load(f)
```

### Frontend Data (M3)
```javascript
// Career options: Object.keys(jobRoles)
// Skills for career: jobRoles[selectedCareer]
// Courses for skill: courses[selectedSkill]
```

## 🎯 Project Status
- ✅ **AI Agents Complete** (Multi-agent pipeline with LangGraph)
- ✅ **Data Curation Complete** (89 skills, 200+ courses mapped)
- ✅ **Logging System Complete** (Analytics and performance tracking)
- ✅ **Documentation Complete** (Technical docs and security guidelines)
- 🔄 **Backend API Development** (Flask/FastAPI integration)
- 🔄 **Frontend UI Development** (React components)
- ⏳ **Testing & Integration** (Connecting all components)

## 📄 License
MIT License - see [LICENSE](LICENSE) file for details.

---
**🚀 Ready to transform tech careers with AI!**  
Made with ❤️ by the Career Guidance AI Team
