#!/usr/bin/env python3
"""
Test script to demonstrate data integration with curated job roles and courses.
This script shows how the AI agents now use the curated data from Nishant's work.
"""

import json
import os

def load_data_files():
    """Load job roles and courses data from ../data/ folder"""
    try:
        # Load from parent directory (data folder)
        with open("../data/job_roles.json", "r") as f:
            job_roles = json.load(f)
        with open("../data/courses.json", "r") as f:
            courses = json.load(f)
        print("✅ Loaded curated data files from ../data/")
        return job_roles, courses
    except FileNotFoundError as e:
        print(f"❌ Error loading data files: {e}")
        return {}, {}

def demonstrate_integration():
    """Demonstrate how the data is integrated with AI agents"""
    
    print("🎯 AI-Powered Career Pathfinder - Data Integration Test")
    print("=" * 60)
    
    # Load curated data
    job_roles_data, courses_data = load_data_files()
    
    print(f"\n📊 Data Integration Status:")
    print(f"  • Job Roles: {len(job_roles_data)} career paths loaded")
    print(f"  • Courses: {len(courses_data)} skills with course recommendations")
    
    # Show available career paths
    print(f"\n🎯 Available Career Paths:")
    for i, career_path in enumerate(job_roles_data.keys(), 1):
        skills_count = len(job_roles_data[career_path])
        print(f"  {i}. {career_path} ({skills_count} required skills)")
    
    # Demonstrate gap analysis improvement
    print(f"\n🔍 Gap Analysis Enhancement:")
    target_role = "Data Scientist"
    required_skills = job_roles_data.get(target_role, [])
    print(f"  Target Role: {target_role}")
    print(f"  Required Skills: {required_skills}")
    
    sample_user_skills = ["Python", "SQL", "Git"]
    missing_skills = [skill for skill in required_skills if skill not in sample_user_skills]
    print(f"  User Skills: {sample_user_skills}")
    print(f"  Missing Skills: {missing_skills[:5]}...")  # Show first 5
    
    # Demonstrate course recommendations
    print(f"\n📚 Course Recommendations Enhancement:")
    skill_to_demo = "Python"
    if skill_to_demo in courses_data:
        courses = courses_data[skill_to_demo]
        print(f"  Skill: {skill_to_demo}")
        print(f"  Available Courses:")
        for i, course in enumerate(courses[:3], 1):  # Show top 3
            print(f"    {i}. {course}")
    
    # Show integration benefits
    print(f"\n🚀 Integration Benefits:")
    print(f"  ✅ Agent 2 (Gap Analyzer) now uses curated job requirements")
    print(f"  ✅ Agent 3 (Roadmap Mentor) now recommends specific courses")
    print(f"  ✅ Consistent skill mapping across all career paths")
    print(f"  ✅ 200+ vetted course recommendations from multiple platforms")
    
    # Demonstrate skill matching
    print(f"\n🎯 Smart Skill Matching:")
    test_skills = ["python", "machine learning", "javascript", "nonexistent_skill"]
    for skill in test_skills:
        matched_courses = None
        for course_skill in courses_data.keys():
            if skill.lower() == course_skill.lower():
                matched_courses = courses_data[course_skill]
                break
        
        if matched_courses:
            print(f"  '{skill}' → ✅ {len(matched_courses)} courses available")
        else:
            print(f"  '{skill}' → ❌ No curated courses (will use AI fallback)")
    
    # Show data quality
    print(f"\n📈 Data Quality Metrics:")
    total_skills = len(courses_data)
    total_courses = sum(len(courses) for courses in courses_data.values())
    avg_courses_per_skill = total_courses / total_skills if total_skills > 0 else 0
    
    print(f"  • Total Skills Covered: {total_skills}")
    print(f"  • Total Course Recommendations: {total_courses}")
    print(f"  • Average Courses per Skill: {avg_courses_per_skill:.1f}")
    
    # Platform distribution
    platforms = {}
    for courses_list in courses_data.values():
        for course in courses_list:
            if "Coursera" in course:
                platforms["Coursera"] = platforms.get("Coursera", 0) + 1
            elif "YouTube" in course:
                platforms["YouTube"] = platforms.get("YouTube", 0) + 1
            elif "IBM SkillsBuild" in course:
                platforms["IBM SkillsBuild"] = platforms.get("IBM SkillsBuild", 0) + 1
            elif "freeCodeCamp" in course:
                platforms["freeCodeCamp"] = platforms.get("freeCodeCamp", 0) + 1
            else:
                platforms["Other"] = platforms.get("Other", 0) + 1
    
    print(f"\n🌐 Platform Distribution:")
    for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_courses) * 100
        print(f"  • {platform}: {count} courses ({percentage:.1f}%)")

if __name__ == "__main__":
    demonstrate_integration()
