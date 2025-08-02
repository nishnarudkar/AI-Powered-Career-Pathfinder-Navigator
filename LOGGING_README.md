# Career Pathfinder Logging System

This directory contains a comprehensive logging system for the AI-Powered Career Pathfinder Navigator that captures and analyzes pipeline executions.

## Files Overview

### Core Files

- `career_pathfinder_langgraph.py` - Main pipeline with integrated logging support
- `career_logger.py` - Logging system implementation
- `view_logs.py` - Log viewer and analysis utility
- `career_pathfinder_logs.json` - JSON log file (auto-generated)

## Features

### 🔍 Automatic Logging

The main pipeline can automatically log executions when `log_execution=True`:

```python
from career_pathfinder_langgraph import run_pipeline

result = run_pipeline(
    input="Experienced in python and sql, built dashboards.",
    target_role="Data Scientist",
    log_execution=True  # Enable logging
)
```

### 📊 Log Structure

Each log entry contains:

- **Timestamp**: When the execution occurred
- **Input**: User's profile text and target role
- **Output Summary**: Counts and key metrics
- **Full Result**: Complete pipeline output including roadmaps
- **Execution Time**: Performance metrics
- **Session ID**: Unique identifier

### 📈 Analytics

The logging system provides:

- **Summary Statistics**: Total executions, common roles, averages
- **Performance Tracking**: Execution times and trends
- **Role Analysis**: Filter by target roles
- **Historical Data**: Complete execution history

## Usage Examples

### Basic Logging

```python
# Run with logging enabled
result = run_pipeline(user_input, target_role, log_execution=True)
```

### View Recent Logs

```bash
python view_logs.py --recent 10
```

### Show Statistics

```bash
python view_logs.py --stats
```

### Filter by Role

```bash
python view_logs.py --role "Data Scientist"
```

### Full Details

```bash
python view_logs.py --full --recent 1
```

### Standalone Logging

```python
from career_logger import CareerPathfinderLogger, save_sample_execution

# Log a sample execution
save_sample_execution()

# Use logger directly
logger = CareerPathfinderLogger()
log_entry = logger.log_execution(input_text, target_role, result, execution_time)
```

## Log File Format

The logs are stored in JSON format with the following structure:

```json
[
  {
    "timestamp": "2025-08-02T09:15:12.399777",
    "input": {
      "text": "Software Engineer with 3 years experience...",
      "target_role": "Senior Full Stack Developer"
    },
    "output": {
      "extracted_skills": [...],
      "missing_skills": [...],
      "nice_to_have": [...],
      "roadmap_phases": 3,
      "total_recommended_skills": 13
    },
    "full_result": { /* Complete pipeline output */ },
    "execution_time_seconds": 16.678741931915283,
    "session_id": "session_20250802_091512"
  }
]
```

## Benefits

1. **Performance Monitoring**: Track execution times and identify bottlenecks
2. **Usage Analytics**: Understand common target roles and skill patterns
3. **Quality Assurance**: Review pipeline outputs for consistency
4. **Historical Tracking**: Maintain complete execution history
5. **Debugging**: Troubleshoot issues with detailed execution logs
6. **Research**: Analyze trends in career pathfinding requests

## Configuration

The logger uses the following defaults:

- **Log File**: `career_pathfinder_logs.json`
- **Format**: JSON with pretty printing
- **Retention**: No automatic cleanup (manual management)
- **Timezone**: System local time with ISO format

## Advanced Usage

### Custom Log Location

```python
logger = CareerPathfinderLogger("custom_logs.json")
```

### Programmatic Analysis

```python
logger = CareerPathfinderLogger()

# Get statistics
stats = logger.get_summary_stats()

# Filter by role
data_scientist_logs = logger.get_logs_by_target_role("Data Scientist")

# Recent executions
recent = logger.get_recent_logs(10)
```

## Log Viewer Options

The `view_logs.py` script supports multiple viewing modes:

- `--recent N`: Show last N executions
- `--role ROLE`: Filter by target role
- `--stats`: Display summary statistics
- `--full`: Include complete roadmap details

## Sample Output

```
📈 Career Pathfinder Statistics
========================================
Total Executions: 2
Most Common Target Role: Senior Full Stack Developer
Average Extracted Skills: 9.0
Average Missing Skills: 5.5
Date Range: {'first_execution': '2025-08-02T09:15:12.399777', 'last_execution': '2025-08-02T09:17:26.667764'}
```

This logging system provides comprehensive tracking and analysis capabilities for the Career Pathfinder Navigator, enabling continuous improvement and insights into user patterns.
