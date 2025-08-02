#!/usr/bin/env python3
"""
Career Pathfinder Log Viewer
A utility script to view and analyze logged career pathfinder executions
"""

import json
import argparse
from career_logger import CareerPathfinderLogger


def main():
    parser = argparse.ArgumentParser(description="View Career Pathfinder execution logs")
    parser.add_argument("--recent", "-r", type=int, default=5, 
                       help="Show recent N executions (default: 5)")
    parser.add_argument("--role", "-role", type=str, 
                       help="Filter by target role")
    parser.add_argument("--stats", "-s", action="store_true", 
                       help="Show summary statistics")
    parser.add_argument("--full", "-f", action="store_true", 
                       help="Show full results including roadmaps")
    
    args = parser.parse_args()
    
    logger = CareerPathfinderLogger()
    
    if args.stats:
        print("📈 Career Pathfinder Statistics")
        print("=" * 40)
        stats = logger.get_summary_stats()
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print()
    
    if args.role:
        print(f"🎯 Executions for role: {args.role}")
        print("=" * 40)
        logs = logger.get_logs_by_target_role(args.role)
    else:
        print(f"📋 Recent {args.recent} executions")
        print("=" * 40)
        logs = logger.get_recent_logs(args.recent)
    
    if not logs:
        print("No logs found matching the criteria.")
        return
    
    for i, log in enumerate(logs, 1):
        print(f"\n🔍 Execution #{i}")
        print(f"Session ID: {log['session_id']}")
        print(f"Timestamp: {log['timestamp']}")
        print(f"Target Role: {log['input']['target_role']}")
        print(f"Execution Time: {log.get('execution_time_seconds', 'N/A'):.2f}s")
        
        output = log['output']
        print(f"\n📊 Results Summary:")
        print(f"  • Extracted Skills: {len(output['extracted_skills'])} skills")
        print(f"  • Missing Skills: {len(output['missing_skills'])} skills")
        print(f"  • Nice to Have: {len(output['nice_to_have'])} skills")
        print(f"  • Roadmap Phases: {output['roadmap_phases']} phases")
        print(f"  • Total Recommendations: {output['total_recommended_skills']} skills")
        
        if output['extracted_skills']:
            print(f"\n🛠️  Extracted Skills: {', '.join(output['extracted_skills'][:5])}{'...' if len(output['extracted_skills']) > 5 else ''}")
        
        if output['missing_skills']:
            print(f"❌ Missing Skills: {', '.join(output['missing_skills'][:5])}{'...' if len(output['missing_skills']) > 5 else ''}")
        
        if args.full and 'roadmap' in log['full_result']:
            print(f"\n🗺️  Learning Roadmap:")
            for phase in log['full_result']['roadmap']:
                print(f"  📍 {phase['phase']}: {len(phase['items'])} items")
                for item in phase['items']:
                    skill = item.get('skill', 'Unknown')
                    course = item.get('course', {})
                    platform = course.get('platform', 'Unknown')
                    title = course.get('title', 'Unknown')
                    print(f"    • {skill}: {title} ({platform})")
        
        print("-" * 60)


if __name__ == "__main__":
    main()
