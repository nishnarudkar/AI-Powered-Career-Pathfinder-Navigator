# 🚀 AI-Powered Career Pathfinder Navigator

Welcome to the **AI-Powered Career Pathfinder Navigator**!  
This intelligent platform helps tech professionals analyze their skills, identify gaps, and receive personalized learning roadmaps to achieve their dream tech jobs.

---

## ✨ Features

- **📄 Resume Analysis**: Upload your resume (PDF/DOCX) and let the system extract and identify your technical skills.
- **🎯 Target Role Selection**: Choose your desired tech job role from a curated list.
- **🗺️ Personalized Learning Roadmaps**: Get a logical, phased learning plan tailored to bridge your skill gaps.
- **📚 Curated Course Recommendations**: Each roadmap step includes a recommended course to help you progress.
- **🤖 AI Powered**: Built on LangChain, LangGraph, and OpenAI for advanced skill analysis and roadmap generation.
- **🌐 Modern Web UI**: Interactive, responsive interface built with Flask and JavaScript.

---

## 🖼️ Screenshots

> Replace the image links below with your actual screenshots if needed.

### Landing Page
![Landing Page](https://i.imgur.com/rS2UaYy.png)

### Resume Upload & Analysis
![Resume Upload](https://i.imgur.com/rS2UaYy.png)

### Personalized Roadmap Output
![Roadmap Output](https://i.imgur.com/rS2UaYy.png)

---

## 👥 Meet the Team

This project is a team effort!  
**Team Members:**
- [Nishant Narudkar](https://github.com/nishnarudkar) — Backend, AI Integration & Testing
- [Vatsal Parmar](https://github.com/Vatsal211005) — Frontend Development
- [Maitreya Pawar](https://github.com/Metzo64) — Data Curation
- [Saksham Shukla](https://github.com/Saksham-3175) — AI Agents & ML
- [Aamir Sarang](https://github.com/Aamir-Sarang31) — Documentation 

---

## ⚙️ Tech Stack

- **Backend**: Python 3.10+, Flask, LangChain, LangGraph, OpenAI API, PyPDF2, python-docx
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data**: JSON (Courses & Job Roles)
- **Deployment**: virtualenv, Gunicorn/Waitress

---

## 🚀 Getting Started

**Prerequisites**
- Python 3.10+
- [OpenAI API Key](https://platform.openai.com/signup)
- [LangSmith API Key](https://www.langchain.com/langsmith) (optional)

**Installation**
```sh
git clone https://github.com/nishnarudkar/AI-Powered-Career-Pathfinder-Navigator.git
cd AI-Powered-Career-Pathfinder-Navigator/development
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

**Set Environment Variables**
Create `.env` in `development` folder:
```
OPENAI_API_KEY="your_openai_api_key_here"
LANGSMITH_API_KEY="your_langsmith_api_key_here"
```

**Run the Application**
```sh
flask run
# or
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📂 Project Structure

```
/ai-career-pathfinder
│
├── frontend/
│   ├── static/
│   │   ├── styles.css
│   │   └── script.js
│   └── templates/
│       └── index.html
│
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── career_logger.py            # Utility for logging
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # (You create this) For API keys
│   │
│   ├── agents/
│   │   └── career_pathfinder_langgraph.py # The core AI agent logic
│   │
│   ├── data/
│   │   ├── courses.json
│   │   └── job_roles.json
│   │
│   └── uploads/                    # For temporarily storing resumes
│
├── docs/
│   └── (e.g., architecture.md)     # For project documentation, diagrams, etc.
│
└── README.md                      
```

---

## 🙏 Acknowledgements

- Inspired by the need for accessible, personalized career guidance for tech professionals.
- Thanks to the teams behind [LangChain](https://www.langchain.com/) and [OpenAI](https://openai.com/) for making this possible.

---
