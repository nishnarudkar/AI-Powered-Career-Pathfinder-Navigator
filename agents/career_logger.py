import json
import datetime
from pathlib import Path


class CareerPathfinderLogger:
    """Logger for career pathfinder pipeline executions"""
    
    def __init__(self, log_file="career_pathfinder_logs.json"):
        self.log_file = Path(log_file)
        self.logs = self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing logs from file if it exists"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def log_execution(self, input_text: str, target_role: str, result: dict, execution_time: float = None):
        """Log a pipeline execution"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "input": {
                "text": input_text,
                "target_role": target_role
            },
            "output": {
                "extracted_skills": result.get("extracted_skills", []),
                "missing_skills": result.get("missing_skills", []),
                "nice_to_have": result.get("nice_to_have", []),
                "roadmap_phases": len(result.get("roadmap", [])),
                "total_recommended_skills": len(result.get("missing_skills", [])) + len(result.get("nice_to_have", []))
            },
            "full_result": result,
            "execution_time_seconds": execution_time,
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        return log_entry
    
    def _save_logs(self):
        """Save logs to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2)
    
    def get_recent_logs(self, count: int = 5):
        """Get the most recent log entries"""
        return self.logs[-count:] if len(self.logs) >= count else self.logs
    
    def get_logs_by_target_role(self, target_role: str):
        """Get logs filtered by target role"""
        return [log for log in self.logs if log["input"]["target_role"].lower() == target_role.lower()]
    
    def get_summary_stats(self):
        """Get summary statistics from all logs"""
        if not self.logs:
            return {"total_executions": 0}
        
        total_executions = len(self.logs)
        target_roles = [log["input"]["target_role"] for log in self.logs]
        most_common_role = max(set(target_roles), key=target_roles.count) if target_roles else None
        
        avg_extracted_skills = sum(len(log["output"]["extracted_skills"]) for log in self.logs) / total_executions
        avg_missing_skills = sum(len(log["output"]["missing_skills"]) for log in self.logs) / total_executions
        
        return {
            "total_executions": total_executions,
            "most_common_target_role": most_common_role,
            "average_extracted_skills": round(avg_extracted_skills, 2),
            "average_missing_skills": round(avg_missing_skills, 2),
            "date_range": {
                "first_execution": self.logs[0]["timestamp"],
                "last_execution": self.logs[-1]["timestamp"]
            }
        }


# Example usage function
def save_sample_execution():
    """Save the sample execution from the main module"""
    from career_pathfinder_optimized import run_pipeline
    import time
    
    logger = CareerPathfinderLogger()
    
    # Sample input data
    sample_input = """
    Software Engineer with 3 years experience
    Skills: Python, JavaScript, React, Node.js, MongoDB, Git
    Experience: Built web applications, REST APIs, worked with databases
    Education: Computer Science degree
    """
    
    sample_target_role = "Senior Full Stack Developer"
    
    print("Executing career pathfinder pipeline...")
    start_time = time.time()
    
    # Run the pipeline
    result = run_pipeline(sample_input, sample_target_role)
    
    execution_time = time.time() - start_time
    
    # Log the execution
    log_entry = logger.log_execution(
        input_text=sample_input.strip(),
        target_role=sample_target_role,
        result=result,
        execution_time=execution_time
    )
    
    print(f"✅ Execution logged successfully!")
    print(f"📊 Session ID: {log_entry['session_id']}")
    print(f"⏱️  Execution time: {execution_time:.2f} seconds")
    print(f"📁 Log saved to: {logger.log_file}")
    
    # Display summary
    stats = logger.get_summary_stats()
    print("\n📈 Summary Statistics:")
    print(json.dumps(stats, indent=2))
    
    return log_entry


if __name__ == "__main__":
    save_sample_execution()
