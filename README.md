# 🚀 Career Guidance AI Platform

## 📖 Project Overview
An intelligent career guidance platform that helps tech professionals identify skill gaps and get personalized learning recommendations using AI agents.

## ✨ Features
- 🔍 **Skill Gap Analysis**: Compare your skills with job requirements
- 🎯 **Personalized Learning Paths**: AI-curated course recommendations  
- 📊 **Career Roadmaps**: Visual progression paths for 6+ tech careers
- 🤖 **Resume Parsing**: Automatic skill extraction from resumes
- 📈 **Progress Tracking**: Monitor your learning journey

## 🛠️ Tech Stack
- **Backend**: Python, Flask/FastAPI
- **Frontend**: React, Tailwind CSS
- **AI/ML**: OpenAI GPT, scikit-learn, NLTK
- **Database**: MongoDB/PostgreSQL
- **Data**: JSON-based skill and course mappings

## 👥 Team Structure
| Role | Member | Folder | Responsibilities |
|------|--------|--------|------------------|
| **M1** | Backend Lead | `/backend` | API development, database, server setup |
| **M2** | AI Agent Developer | `/ai-agents` | Gap analysis, learning path, NLP agents |
| **M3** | Frontend Developer | `/frontend` | React UI, user experience, dashboard |
| **M4** | Data Curator | `/data` | Job roles, skills mapping, course curation ✅ |
| **M5** | Documentation | `/docs` | Technical docs, user guides, presentations |

## 🎯 Supported Career Paths
- 📊 **Data Scientist** (14 skills mapped)
- 💻 **Full Stack Web Developer** (15 skills mapped)
- 🤖 **AI/ML Engineer** (15 skills mapped)
- ⚙️ **DevOps Engineer** (15 skills mapped)
- 🔒 **Cybersecurity Analyst** (15 skills mapped)
- 📱 **Mobile App Developer** (15 skills mapped)

## 📊 Dataset Overview
- **89 Technical Skills** mapped across 6 career paths
- **200+ Learning Resources** from IBM SkillsBuild, Coursera, YouTube
- **70% Free Resources** ensuring accessibility
- **JSON-based structure** optimized for AI agent integration

## 🚀 Quick Start

### Prerequisites
```bash
- Python 3.8+
- Node.js 16+
- Git
```

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME

# Backend setup (M1's work)
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup (M3's work)  
cd ../frontend
npm install
npm start

# AI Agents (M2's work)
cd ../ai-agents
pip install -r requirements.txt
python gap_analysis_agent.py
```

## 🔧 API Endpoints (Planned)
```
POST /api/analyze-skills    # Skill gap analysis
POST /api/learning-path     # Get personalized recommendations
POST /api/upload-resume     # Resume parsing and skill extraction  
GET  /api/career-paths      # Available career paths
GET  /api/courses          # Course recommendations by skill
```

## 📁 Project Structure
```
career-guidance-ai/
├── data/           # ✅ Complete - Skills & courses dataset
├── backend/        # 🔄 M1 - API and database development
├── frontend/       # 🔄 M3 - React UI development  
├── ai-agents/      # 🔄 M2 - AI agents implementation
├── docs/           # 🔄 M5 - Documentation and guides
└── deployment/     # ⏳ Team - Deployment configuration
```

## 🤝 Contributing
1. Accept collaboration invitation (check email)
2. Clone repository: `git clone [repo-url]`
3. Create feature branch: `git checkout -b feature/your-feature`
4. Work in your assigned folder
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/your-feature`
7. Create Pull Request for review

## 📚 Data Access for Developers

### Backend Integration (M1)
```python
import json
with open('data/job_roles.json') as f:
    job_roles = json.load(f)
with open('data/courses.json') as f:
    courses = json.load(f)
```

### AI Agent Usage (M2)
```python
# Gap Analysis
user_skills = ["Python", "SQL"] 
required_skills = job_roles["Data Scientist"]
gaps = [skill for skill in required_skills if skill not in user_skills]

# Learning Recommendations  
recommended_courses = courses[gaps[0]]
```

### Frontend Data (M3)
```javascript
// Career options: Object.keys(jobRoles)
// Skills for career: jobRoles[selectedCareer]
// Courses for skill: courses[selectedSkill]
```

## 🎯 Project Status
- ✅ **Data Curation Complete** (89 skills, 200+ courses mapped)
- 🔄 **AI Agents in Development** (Gap analysis, learning paths)
- 🔄 **Backend API Development** (Flask/FastAPI setup)
- 🔄 **Frontend UI Development** (React components)
- ⏳ **Testing & Integration** (Connecting all components)

## 📄 License
MIT License - see [LICENSE](LICENSE) file for details.

---
**🚀 Ready to transform tech careers with AI!**  
Made with ❤️ by the Career Guidance AI Team
