# 🚀 AI Career Pathfinder

Welcome to the AI Career Pathfinder! This intelligent web application helps users chart a personalized journey to their dream tech career. By analyzing a user's resume, the application identifies existing skills, and then generates a custom, step-by-step learning roadmap to bridge the gap to their desired job role, complete with curated course recommendations.

![AI Career Pathfinder Screenshot](https://i.imgur.com/rS2UaYy.png)

---

## ✨ Features

* **📄 Intelligent Resume Analysis**: Upload your resume in PDF or DOCX format. The app automatically extracts and identifies your key technical skills.
* **🎯 Target Role Selection**: Choose from a list of popular tech job roles that you aspire to.
* **🗺️ Dynamic Learning Roadmaps**: Generates a personalized, phased learning plan based on the gap between your current skills and the requirements of your target role.
* **📚 Curated Course Recommendations**: Each step in the roadmap includes a specific, relevant course suggestion to help you learn the required skill.
* **🤖 Powered by Large Language Models**: Utilizes the power of LangChain and OpenAI to understand skills, analyze job requirements, and build logical learning paths.
* **🌐 Interactive Web Interface**: A sleek, modern, and user-friendly interface built with Flask and JavaScript.

---

## ⚙️ How It Works

The application follows a simple, three-step process to create your personalized roadmap:

1.  **Upload Your Resume**: The user uploads their resume. The Flask backend processes the file, extracts the raw text, and prepares it for analysis.
2.  **Select Target Job Role**: The user selects their desired job role from a dropdown menu. The application then uses its AI pipeline to analyze the user's extracted resume text to identify a list of current skills.
3.  **Generate Learning Roadmap**: With the current skills and the target role identified, the user clicks "Generate". The backend sends this information to the core AI pipeline, which:
    * Compares the user's skills to the required skills for the target role.
    * Identifies the knowledge gap.
    * Generates a logical, step-by-step roadmap to fill that gap.
    * Suggests relevant online courses for each skill in the roadmap.
    * Sends the complete roadmap back to the frontend to be displayed in a timeline format.

---

## 🛠️ Tech Stack

This project is built with a modern stack, combining a Python backend for AI processing with a dynamic HTML/CSS/JS frontend.

* **Backend**:
    * **[Flask](https://flask.palletsprojects.com/)**: A lightweight web framework for Python.
    * **[LangChain](https://www.langchain.com/)**: A framework for developing applications powered by language models.
    * **[LangGraph](https://langchain-ai.github.io/langgraph/)**: A library for building stateful, multi-actor applications with LLMs.
    * **[OpenAI API](https://beta.openai.com/docs/)**: Used for the core intelligence of the application.
    * **[PyPDF2](https://pypdf2.readthedocs.io/) & [python-docx](https://python-docx.readthedocs.io/)**: For extracting text from uploaded resumes.

* **Frontend**:
    * **HTML5**
    * **CSS3** (with modern styling and animations)
    * **JavaScript (ES6+)**: For dynamic interactions and API communication (`fetch`).

* **Development & Deployment**:
    * **Python 3.10+**
    * **virtualenv**: For managing project dependencies.
    * **Gunicorn / Waitress**: (Recommended for production deployment).

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.10 or higher
* An API Key from [OpenAI](https://platform.openai.com/signup)
* An API Key from [LangSmith](https://www.langchain.com/langsmith) (Optional, for tracing)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/ai-career-pathfinder.git](https://github.com/your-username/ai-career-pathfinder.git)
    cd ai-career-pathfinder
    ```

2.  **Navigate to the backend and set up the environment:**
    ```sh
    cd backend
    ```
    * **Create and activate a virtual environment:**
        * On macOS/Linux:
            ```sh
            python3 -m venv venv
            source venv/bin/activate
            ```
        * On Windows:
            ```sh
            python -m venv venv
            .\venv\Scripts\activate
            ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    * Create a new file named `.env` in the `backend` directory.
    * Add your API keys to this file:
        ```
        OPENAI_API_KEY="your_openai_api_key_here"
        LANGSMITH_API_KEY="your_langsmith_api_key_here"
        ```

### Running the Application

1.  **Start the Flask server from the `backend` directory:**
    ```sh
    # Make sure you are in the /backend directory
    flask run
    ```
    Or, more explicitly:
    ```sh
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` and you should see the application running!

---

## 📂 Project Structure

Here is an overview of the new, organized project structure:


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
└── README.md                       # This file


---

## 🙏 Acknowledgements

* This project was inspired by the need for personalized career guidance in the ever-evolving tech industry.
* Special thanks to the teams behind LangChain and OpenAI for their incredible tools.
