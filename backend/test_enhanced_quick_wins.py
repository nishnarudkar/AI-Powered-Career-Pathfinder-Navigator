#!/usr/bin/env python3
"""
Test script for enhanced quick-win recommendations with micro-tasks and course IDs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from role_readiness_agent import RoleReadinessAgent

def test_enhanced_quick_wins():
    """Test the enhanced quick-win recommendation system"""
    
    print("🎯 Enhanced Quick-Win Recommendations Test")
    print("=" * 60)
    
    agent = RoleReadinessAgent()
    
    # Test different skill profiles to see various recommendation types
    test_profiles = [
        {
            "name": "Beginner Data Scientist",
            "skills": ["python", "excel"],  # Missing many foundational skills
            "target_role": "data-scientist"
        },
        {
            "name": "Intermediate Developer", 
            "skills": ["python", "javascript", "html", "css", "git"],  # Missing some advanced skills
            "target_role": "full-stack-developer"
        },
        {
            "name": "DevOps Beginner",
            "skills": ["linux", "git"],  # Missing container and automation skills
            "target_role": "devops-engineer"
        }
    ]
    
    for profile in test_profiles:
        print(f"\n👤 Profile: {profile['name']}")
        print(f"Current Skills: {', '.join(profile['skills'])}")
        print(f"Target Role: {profile['target_role'].replace('-', ' ').title()}")
        print("-" * 50)
        
        # Get role assessment
        assessment = agent.assess_from_raw_skills(profile['skills'])
        
        # Find the target role assessment
        target_assessment = None
        for role in assessment.get('matched_roles', []):
            if role['role_name'] == profile['target_role']:
                target_assessment = role
                break
        
        if target_assessment:
            readiness_pct = int(target_assessment['readiness_score'] * 100)
            print(f"Readiness: {readiness_pct}% ({target_assessment['readiness_label']})")
            print(f"Missing Skills: {len(target_assessment['missing_skills'])} total")
            
            print("\n🚀 Quick-Win Recommendations:")
            for i, rec in enumerate(target_assessment['quick_win_recommendations'], 1):
                print(f"{i}. {rec}")
        
        print()

def test_specific_micro_tasks():
    """Test specific micro-task recommendations for different skills"""
    
    print("\n🔬 Micro-Task Recommendations by Skill")
    print("=" * 50)
    
    agent = RoleReadinessAgent()
    
    # Test skills that should trigger micro-tasks (small gaps)
    test_skills_sets = [
        {
            "name": "Python Developer (needs SQL)",
            "skills": ["python", "javascript", "git"],  # Missing SQL - should get micro-task
        },
        {
            "name": "Frontend Developer (needs backend)",
            "skills": ["html", "css", "javascript", "react"],  # Missing backend - should get courses
        },
        {
            "name": "ML Practitioner (needs stats)",
            "skills": ["python", "machine-learning", "pandas", "numpy"],  # Missing stats - should get micro-task
        }
    ]
    
    for test_case in test_skills_sets:
        print(f"\n📊 Test Case: {test_case['name']}")
        print(f"Skills: {', '.join(test_case['skills'])}")
        
        # Get assessment for data scientist role (comprehensive requirements)
        assessment = agent.assess_from_raw_skills(test_case['skills'])
        data_scientist_role = next((r for r in assessment['matched_roles'] if r['role_name'] == 'data-scientist'), None)
        
        if data_scientist_role:
            print("Quick Wins:")
            for rec in data_scientist_role['quick_win_recommendations']:
                # Highlight if it's a micro-task (contains specific hour estimates or actions)
                if any(indicator in rec.lower() for indicator in ['write', 'build', 'create', 'implement', 'practice']):
                    print(f"  🎯 MICRO-TASK: {rec}")
                else:
                    print(f"  📚 COURSE: {rec}")

def show_course_catalog_summary():
    """Show summary of available courses and micro-tasks"""
    
    print("\n📚 Enhanced Course Catalog Summary")
    print("=" * 40)
    
    agent = RoleReadinessAgent()
    
    print("Available Skills with Micro-Tasks and Courses:")
    for skill, catalog_entry in agent.course_catalog.items():
        courses_count = len(catalog_entry.get('courses', []))
        micro_tasks_count = len(catalog_entry.get('micro_tasks', []))
        
        print(f"\n🔧 {skill.replace('-', ' ').title()}:")
        print(f"   📚 {courses_count} courses available")
        print(f"   🎯 {micro_tasks_count} micro-tasks available")
        
        # Show first micro-task as example
        if catalog_entry.get('micro_tasks'):
            print(f"   Example micro-task: {catalog_entry['micro_tasks'][0]}")

if __name__ == "__main__":
    test_enhanced_quick_wins()
    test_specific_micro_tasks()
    show_course_catalog_summary()
    
    print("\n✅ Enhanced Quick-Win System Features:")
    print("   🎯 Specific micro-tasks for quick skill gaps")
    print("   📚 Course recommendations with IDs and duration")
    print("   ⚡ Actionable tasks with time estimates")
    print("   🎨 Smart fallbacks for uncataloged skills")
    print("   📊 Gap-based recommendation strategy")
