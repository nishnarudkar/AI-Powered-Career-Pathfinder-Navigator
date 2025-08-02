# AI-Powered-Career-Pathfinder-Navigator

🚀 AI-powered career guidance platform that analyzes skill gaps and recommends personalized learning paths for tech professionals.  🔧 Tech Stack: Python, Flask/FastAPI, React, NLP, Machine Learning 👥 Team Project: 5 members working on Backend, Frontend, AI Agents, Data Curation, Documentation

## Usage

```python
from career_pathfinder_langgraph import run_pipeline
out = run_pipeline(
    input="Experienced in python and sql, built dashboards.",
    target_role="Data Scientist"
)
print(out["roadmap"][0])
```
