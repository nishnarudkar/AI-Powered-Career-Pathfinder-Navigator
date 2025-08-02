# AI-Powered Career Pathfinder Navigator - Technical Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [File Structure](#file-structure)
5. [Installation & Setup](#installation--setup)
6. [Core Components](#core-components)
7. [API Reference](#api-reference)
8. [Logging System](#logging-system)
9. [Usage Examples](#usage-examples)
10. [Development Guidelines](#development-guidelines)
11. [Troubleshooting](#troubleshooting)

## 🎯 Project Overview

The AI-Powered Career Pathfinder Navigator is an intelligent system that analyzes a user's current skills and provides personalized learning roadmaps to help them transition to their target role. The system uses multiple AI agents working in sequence to extract skills, analyze gaps, and create detailed learning recommendations.

### Key Features

- **Skill Extraction**: Automatically identifies technical skills from resume/CV text
- **Gap Analysis**: Compares current skills with target role requirements
- **Learning Roadmap**: Creates a 3-phase learning plan with specific course recommendations
- **Comprehensive Logging**: Tracks all executions with detailed analytics
- **JSON-based Output**: Structured data for easy integration

## 🏗️ Architecture

The system follows a **Multi-Agent Pipeline Architecture** using LangGraph:

```
Input → Agent 1 → Agent 2 → Agent 3 → Output
        ↓         ↓         ↓
    Skill      Gap      Roadmap
   Extract   Analysis   Creation
```

### Agent Flow

1. **Agent 1 (Skill Extractor)**: Processes user input and extracts technical skills
2. **Agent 2 (Gap Analyzer)**: Compares extracted skills with target role requirements
3. **Agent 3 (Roadmap Mentor)**: Creates a structured learning roadmap with course recommendations

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.12+**: Primary programming language
- **LangGraph**: Multi-agent workflow orchestration
- **LangChain**: AI agent framework and utilities
- **OpenAI GPT-4o**: Large language model for AI agents
- **LangSmith**: Monitoring and observability (optional)

### Dependencies

```
langgraph>=0.6.2          # Multi-agent workflow engine
langchain>=0.3.27         # AI agent framework
langchain-openai>=0.3.28  # OpenAI integration
openai>=1.98.0            # OpenAI API client
python-dotenv>=1.1.1      # Environment variable management
```

### Development Tools

- **JSON**: Data serialization and logging
- **TypedDict**: Type safety for state management
- **argparse**: Command-line interface for utilities
- **pathlib**: File system operations

## 📁 File Structure

```
AI-Powered-Career-Pathfinder-Navigator/
├── career_pathfinder_langgraph.py    # Main pipeline implementation
├── career_logger.py                  # Logging system
├── view_logs.py                      # Log viewer utility
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── .env                             # Environment variables (ignored by git)
├── career_pathfinder_logs.json     # Execution logs (auto-generated)
├── README.md                        # Project overview
├── LOGGING_README.md               # Logging system documentation
├── documentation.md                # This technical documentation
├── LICENSE                         # Project license
└── .gitignore                     # Git ignore rules
```

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.12 or higher
- OpenAI API account with GPT-4o access
- LangSmith account (optional, for monitoring)

### Step 1: Clone Repository

```bash
git clone https://github.com/nishnarudkar/AI-Powered-Career-Pathfinder-Navigator.git
cd AI-Powered-Career-Pathfinder-Navigator
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:

   ```
   OPENAI_API_KEY=sk-proj-your-openai-key-here
   LANGSMITH_API_KEY=lsv2_pt_your-langsmith-key-here
   ```

### Step 4: Verify Installation

```bash
python career_pathfinder_langgraph.py
```

## 🔧 Core Components {#core-components}

### 1. State Management (`MyState`)

```python
class MyState(TypedDict):
    input: str                    # User's resume/CV text
    target_role: str             # Desired job role
    extracted_skills: list[str]  # Skills found in input
    missing_skills: list[str]    # Skills needed for target role
    nice_to_have: list[str]     # Additional beneficial skills
    roadmap: list[dict]         # Learning roadmap with courses
```

### 2. Agent Functions

#### Agent 1: Skill Extractor

- **Purpose**: Extract technical skills from user input
- **Input**: Raw resume/CV text
- **Output**: Normalized list of skills (max 30, snake_case)
- **Model**: GPT-4o with temperature=0

#### Agent 2: Gap Analyzer

- **Purpose**: Compare user skills with target role requirements
- **Input**: Extracted skills + target role
- **Output**: Missing skills and nice-to-have skills
- **Constraints**: Alphabetical lists, max 10 nice-to-have items

#### Agent 3: Roadmap Mentor

- **Purpose**: Create structured learning roadmap
- **Input**: Missing skills + nice-to-have skills
- **Output**: 3-phase roadmap with course recommendations
- **Format**: Each recommendation includes platform, title, URL, and rationale

### 3. Pipeline Execution

```python
def run_pipeline(input: str, target_role: str, log_execution: bool = False) -> dict:
    # Creates StateGraph workflow
    # Executes agents in sequence
    # Returns complete results
    # Optionally logs execution
```

## 📚 API Reference

### Main Function

```python
run_pipeline(
    input: str,           # User's resume/CV text
    target_role: str,     # Target job role
    log_execution: bool = False  # Enable logging
) -> dict                # Complete pipeline results
```

### Example Response

```json
{
  "input": "Software Engineer with Python experience...",
  "target_role": "Senior Full Stack Developer",
  "extracted_skills": ["python", "javascript", "react"],
  "missing_skills": ["docker", "kubernetes", "aws"],
  "nice_to_have": ["graphql", "typescript", "ci/cd"],
  "roadmap": [
    {
      "phase": "Phase 1",
      "items": [
        {
          "skill": "docker",
          "course": {
            "platform": "Udemy",
            "title": "Docker Deep Dive",
            "url": "https://...",
            "why": "Essential for containerization..."
          }
        }
      ]
    }
  ]
}
```

## 📊 Logging System

### Logger Class

```python
CareerPathfinderLogger(log_file="career_pathfinder_logs.json")
```

### Key Methods

- `log_execution()`: Record pipeline execution
- `get_recent_logs()`: Retrieve recent executions
- `get_logs_by_target_role()`: Filter by target role
- `get_summary_stats()`: Analytics and statistics

### Log Entry Structure

```json
{
  "timestamp": "2025-08-02T09:15:12.399777",
  "input": {...},
  "output": {...},
  "full_result": {...},
  "execution_time_seconds": 16.68,
  "session_id": "session_20250802_091512"
}
```

### Log Viewer Commands

```bash
# View recent executions
python view_logs.py --recent 10

# Show statistics
python view_logs.py --stats

# Filter by role
python view_logs.py --role "Data Scientist"

# Full details with roadmaps
python view_logs.py --full
```

## 💡 Usage Examples

### Basic Usage

```python
from career_pathfinder_langgraph import run_pipeline

result = run_pipeline(
    input="Python developer with 3 years experience in web development",
    target_role="Data Scientist"
)
print(result["roadmap"][0])  # First phase of roadmap
```

### With Logging

```python
result = run_pipeline(
    input="Frontend developer with React experience",
    target_role="Full Stack Developer",
    log_execution=True
)
```

### Standalone Logging

```python
from career_logger import CareerPathfinderLogger

logger = CareerPathfinderLogger()
logger.log_execution(input_text, target_role, result, execution_time)
stats = logger.get_summary_stats()
```

## 👥 Development Guidelines

### Code Style

- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions (snake_case for variables/functions)
- Add docstrings to all functions and classes
- Handle exceptions gracefully with fallback behavior

### Error Handling

- All agents include JSON parsing error handling
- Fallback values prevent pipeline failures
- Debug output helps troubleshoot issues
- Graceful degradation when external services fail

### Testing Strategy

- Test each agent individually
- Verify JSON schema compliance
- Test with various input formats
- Monitor execution times and performance

### Adding New Features

1. Follow the existing agent pattern
2. Update the `MyState` TypedDict if needed
3. Add appropriate error handling
4. Include logging support
5. Update documentation

## 🔍 Troubleshooting

### Common Issues

#### 1. Missing API Keys

**Error**: `ValueError: OPENAI_API_KEY environment variable is required`
**Solution**: Ensure `.env` file exists with valid API keys

#### 2. Import Errors

**Error**: `ModuleNotFoundError: No module named 'langchain_openai'`
**Solution**: Install missing dependencies:

```bash
pip install -r requirements.txt
```

#### 3. JSON Parsing Errors

**Symptom**: Empty results arrays
**Solution**: Check agent debug output, verify API responses

#### 4. Execution Timeouts

**Symptom**: Long execution times (>30s)
**Solution**: Check internet connection, verify API key limits

### Debug Mode

Enable debug output by examining agent responses:

```python
# Add print statements in agent functions
print(f"Agent response: {response.content}")
```

### Performance Optimization

- Use temperature=0 for consistent results
- Implement caching for repeated queries
- Monitor API usage and costs
- Consider batch processing for multiple users

## 📈 Analytics & Monitoring

### Built-in Analytics

- Execution time tracking
- Success/failure rates
- Common target roles
- Average skill counts
- Usage patterns over time

### LangSmith Integration

- Enable detailed tracing of agent interactions
- Monitor token usage and costs
- Track model performance metrics
- Debug complex workflow issues

### Custom Metrics

```python
# Example: Track specific metrics
logger = CareerPathfinderLogger()
stats = logger.get_summary_stats()
print(f"Average execution time: {stats.get('avg_execution_time', 'N/A')}")
```

## 🚀 Deployment Considerations

### Production Setup

- Use environment-specific `.env` files
- Implement rate limiting for API calls
- Add monitoring and alerting
- Consider scaling with multiple API keys
- Implement caching layer for common queries

### Security

- Never commit `.env` files to version control
- Rotate API keys regularly
- Implement input validation and sanitization
- Monitor for unusual usage patterns

### Scalability

- Consider async execution for multiple users
- Implement queue system for high-volume usage
- Add database storage for logs and results
- Use load balancing for API requests

---

## 📞 Support

For technical questions or issues:

1. Check this documentation first
2. Review the troubleshooting section
3. Examine log files for error details
4. Contact the development team with specific error messages

**Repository**: <https://github.com/nishnarudkar/AI-Powered-Career-Pathfinder-Navigator>
**Team**: 5 members (Backend, Frontend, AI Agents, Data Curation, Documentation)

---

*Last Updated: August 2, 2025*
*Version: 1.0.0*
