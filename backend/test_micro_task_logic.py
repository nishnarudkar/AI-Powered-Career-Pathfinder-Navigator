#!/usr/bin/env python3
"""
Targeted test to demonstrate micro-task recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from role_readiness_agent import RoleReadinessAgent, UserSkill, MissingSkill, SkillImportance

def test_micro_task_scenarios():
    """Test scenarios that should trigger micro-tasks vs courses"""
    
    print("🎯 Micro-Task vs Course Recommendation Logic")
    print("=" * 60)
    
    agent = RoleReadinessAgent()
    
    # Create mock missing skills with different gap sizes
    test_scenarios = [
        {
            "name": "Small Gap (Should get micro-task)",
            "missing_skill": MissingSkill(
                skill="sql",
                current_level=2,  # Already intermediate
                target_level=3,   # Need advanced
                gap_degree=1,     # Small gap
                importance=SkillImportance.MUST
            )
        },
        {
            "name": "Large Gap (Should get course)",
            "missing_skill": MissingSkill(
                skill="sql", 
                current_level=0,  # No knowledge
                target_level=3,   # Need advanced
                gap_degree=3,     # Large gap
                importance=SkillImportance.MUST
            )
        },
        {
            "name": "Medium Gap (Should get course)",
            "missing_skill": MissingSkill(
                skill="machine-learning",
                current_level=1,  # Basic knowledge
                target_level=3,   # Need advanced
                gap_degree=2,     # Medium gap
                importance=SkillImportance.MUST
            )
        },
        {
            "name": "Statistics Small Gap (Should get micro-task)",
            "missing_skill": MissingSkill(
                skill="statistics",
                current_level=2,  # Intermediate
                target_level=3,   # Advanced
                gap_degree=1,     # Small gap
                importance=SkillImportance.MUST
            )
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📊 {scenario['name']}")
        missing_skill = scenario['missing_skill']
        print(f"Skill: {missing_skill.skill}")
        print(f"Current Level: {missing_skill.current_level}")
        print(f"Target Level: {missing_skill.target_level}")
        print(f"Gap Degree: {missing_skill.gap_degree}")
        
        # Generate recommendation for this single skill
        recommendations = agent.generate_quick_win_recommendations([missing_skill])
        
        if recommendations:
            rec = recommendations[0]
            print(f"Recommendation: {rec}")
            
            # Identify recommendation type
            if any(keyword in rec.lower() for keyword in ['write', 'build', 'create', 'implement', 'practice', 'do a', 'calculate']):
                print("🎯 Type: MICRO-TASK")
            elif 'course' in rec.lower() and ('id' in rec or 'complete course' in rec):
                print("📚 Type: COURSE")
            else:
                print("📖 Type: GENERAL GUIDANCE")
        else:
            print("❌ No recommendations generated")
        
        print("-" * 40)

def demonstrate_course_id_integration():
    """Show how course IDs are integrated into recommendations"""
    
    print("\n📚 Course ID Integration Examples")
    print("=" * 40)
    
    agent = RoleReadinessAgent()
    
    # Show course catalog structure for a few skills
    example_skills = ["python", "sql", "docker"]
    
    for skill in example_skills:
        if skill in agent.course_catalog:
            catalog = agent.course_catalog[skill]
            print(f"\n🔧 {skill.upper()} Catalog:")
            
            print("Courses:")
            for course in catalog['courses']:
                print(f"   {course['id']}: {course['name']} ({course['duration']}) - {course['provider']}")
            
            print("Micro-tasks:")
            for task in catalog['micro_tasks']:
                print(f"   • {task}")

if __name__ == "__main__":
    test_micro_task_scenarios()
    demonstrate_course_id_integration()
    
    print("\n✅ Enhanced Recommendation Strategy:")
    print("   Gap Degree 1: Micro-task recommendations")
    print("   Gap Degree 2+: Course recommendations with IDs")
    print("   Course catalog includes duration and provider info")
    print("   Actionable tasks with specific time estimates")
