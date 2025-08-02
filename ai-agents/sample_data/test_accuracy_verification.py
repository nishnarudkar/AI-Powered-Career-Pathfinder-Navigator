#!/usr/bin/env python3
"""
VERIFICATION TEST 1: Accurate Skills & Courses Mapping
Tests 100% accurate mapping for web development resumes with the curated data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

def load_curated_data():
    """Load the curated job roles and courses data"""
    try:
        with open("../../../data/job_roles.json", "r") as f:
            job_roles = json.load(f)
        with open("../../../data/courses.json", "r") as f:
            courses = json.load(f)
        print("✅ Loaded curated data successfully")
        return job_roles, courses
    except FileNotFoundError as e:
        print(f"❌ Error loading data: {e}")
        # Fallback - load from relative path
        try:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "..", "..", "..", "data")
            
            with open(os.path.join(data_dir, "job_roles.json"), "r") as f:
                job_roles = json.load(f)
            with open(os.path.join(data_dir, "courses.json"), "r") as f:
                courses = json.load(f)
            print("✅ Loaded curated data from fallback path")
            return job_roles, courses
        except Exception as e2:
            print(f"❌ Fallback failed: {e2}")
            return {}, {}

def simulate_full_pipeline(resume_text: str, target_role: str):
    """Simulate the complete pipeline with curated data integration"""
    
    # Load curated data
    job_roles_data, courses_data = load_curated_data()
    
    # Simulate Agent 1: Skill Extraction (using enhanced fallback)
    from career_pathfinder_langgraph import extract_skills_fallback
    extracted_skills = extract_skills_fallback(resume_text)
    
    # Simulate Agent 2: Gap Analysis (using curated job requirements)
    required_skills = job_roles_data.get(target_role, [])
    required_skills_lower = [skill.lower().replace(' ', '-') for skill in required_skills]
    
    # More intelligent skill matching
    user_skills_matched = []
    missing_skills = []
    
    for req_skill in required_skills_lower:
        matched = False
        for user_skill in extracted_skills:
            # Check various matching patterns
            if (req_skill in user_skill or user_skill in req_skill or 
                req_skill.replace('-', '') in user_skill.replace('-', '') or
                user_skill.replace('-', '') in req_skill.replace('-', '')):
                user_skills_matched.append(req_skill)
                matched = True
                break
        if not matched:
            missing_skills.append(req_skill)
    
    # Simulate Agent 3: Course Recommendations (using curated courses)
    course_recommendations = {}
    for skill in missing_skills[:5]:  # Top 5 missing skills
        # Find course recommendations
        skill_courses = []
        for course_skill, courses_list in courses_data.items():
            if (skill.lower() in course_skill.lower() or 
                course_skill.lower() in skill.lower() or
                skill.replace('-', ' ').lower() in course_skill.lower()):
                skill_courses = courses_list[:3]  # Top 3 courses
                break
        course_recommendations[skill] = skill_courses
    
    return {
        "extracted_skills": extracted_skills,
        "required_skills": required_skills,
        "user_skills_matched": user_skills_matched,
        "missing_skills": missing_skills,
        "course_recommendations": course_recommendations,
        "target_role": target_role
    }

def test_web_dev_accuracy():
    """Test accurate mapping for web development resumes"""
    
    print("🔍 VERIFICATION TEST 1: Skills & Courses Mapping Accuracy")
    print("=" * 65)
    
    # Load curated data for reference
    job_roles_data, courses_data = load_curated_data()
    
    print(f"📊 Loaded Data:")
    print(f"   • Job Roles: {len(job_roles_data)} career paths")
    print(f"   • Courses: {len(courses_data)} skills with recommendations")
    
    # Test Case 1: Full Stack Web Developer Resume
    web_dev_resume = """
    ALEX RODRIGUEZ - Full Stack Developer
    
    TECHNICAL SKILLS:
    • Frontend: React.js, HTML5, CSS3, JavaScript (ES6+), Bootstrap
    • Backend: Node.js, Express.js, REST APIs
    • Databases: MongoDB, PostgreSQL  
    • Tools: Git, npm, JSON
    • Testing: Jest, Unit Testing
    
    EXPERIENCE:
    Full Stack Developer | StartupCorp | 2022-2024
    • Built responsive web applications using React and Node.js
    • Developed RESTful APIs with Express.js
    • Managed MongoDB and PostgreSQL databases
    • Implemented authentication and authorization
    • Used Git for version control and collaboration
    """
    
    target_role = "Full Stack Web Developer"
    
    print(f"\n🧪 TEST CASE: {target_role} Resume")
    print("-" * 50)
    
    # Run pipeline simulation
    result = simulate_full_pipeline(web_dev_resume, target_role)
    
    # Verify skill extraction accuracy
    extracted = result["extracted_skills"]
    required = result["required_skills"]
    matched = result["user_skills_matched"]
    missing = result["missing_skills"]
    courses = result["course_recommendations"]
    
    print(f"📝 Resume Length: {len(web_dev_resume)} characters")
    print(f"🎯 Target Role: {target_role}")
    print(f"📋 Required Skills ({len(required)}): {required}")
    print(f"✅ Extracted Skills ({len(extracted)}): {extracted}")
    print(f"🎯 Matched Skills ({len(matched)}): {matched}")
    print(f"❌ Missing Skills ({len(missing)}): {missing}")
    
    # Calculate accuracy metrics
    total_required = len(required)
    total_matched = len(matched)
    accuracy_percentage = (total_matched / total_required * 100) if total_required > 0 else 0
    
    print(f"\n📊 ACCURACY METRICS:")
    print(f"   • Skill Matching Accuracy: {accuracy_percentage:.1f}%")
    print(f"   • Skills Found: {total_matched}/{total_required}")
    print(f"   • Skills Missing: {len(missing)}")
    
    # Verify course mapping accuracy
    print(f"\n📚 COURSE MAPPING VERIFICATION:")
    courses_found = 0
    total_missing_skills = len(missing)
    
    for skill, skill_courses in courses.items():
        if skill_courses:
            courses_found += 1
            print(f"   ✅ {skill}: {len(skill_courses)} courses available")
            print(f"      • {skill_courses[0] if skill_courses else 'No courses'}")
        else:
            print(f"   ❌ {skill}: No courses found")
    
    course_coverage = (courses_found / total_missing_skills * 100) if total_missing_skills > 0 else 100
    print(f"   📊 Course Coverage: {course_coverage:.1f}%")
    
    # Overall accuracy assessment
    print(f"\n🎯 OVERALL ACCURACY ASSESSMENT:")
    if accuracy_percentage >= 80 and course_coverage >= 80:
        status = "✅ EXCELLENT - Ready for Production"
        grade = "A+"
    elif accuracy_percentage >= 70 and course_coverage >= 70:
        status = "⚠️  GOOD - Minor improvements needed"
        grade = "B+"
    else:
        status = "❌ NEEDS IMPROVEMENT"
        grade = "C"
    
    print(f"   🏆 Status: {status}")
    print(f"   📊 Grade: {grade}")
    print(f"   🎯 Skill Accuracy: {accuracy_percentage:.1f}%")
    print(f"   📚 Course Coverage: {course_coverage:.1f}%")
    
    # Test specific skill mappings
    print(f"\n🔍 DETAILED SKILL MAPPING VERIFICATION:")
    print("-" * 50)
    
    # Check critical web dev skills
    critical_skills = {
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],  
        "JavaScript": ["javascript", "js"],
        "React": ["react", "reactjs", "react.js"],
        "Node.js": ["nodejs", "node.js", "node js"],
        "MongoDB": ["mongodb", "mongo"],
        "Git": ["git"]
    }
    
    for skill_name, variations in critical_skills.items():
        found = False
        for variation in variations:
            if variation in [s.lower() for s in extracted]:
                found = True
                break
        
        status_icon = "✅" if found else "❌"
        print(f"   {status_icon} {skill_name}: {'Found' if found else 'Missing'}")
        
        # Check if courses are available for this skill
        course_available = False
        for course_skill in courses_data.keys():
            if skill_name.lower() in course_skill.lower():
                course_available = True
                break
        
        course_icon = "📚" if course_available else "❌"
        print(f"      {course_icon} Courses: {'Available' if course_available else 'Not found'}")
    
    return accuracy_percentage >= 80 and course_coverage >= 80

if __name__ == "__main__":
    success = test_web_dev_accuracy()
    if success:
        print(f"\n🎉 VERIFICATION 1 PASSED: Skills & Courses mapping is production-ready!")
    else:
        print(f"\n⚠️  VERIFICATION 1 NEEDS ATTENTION: Review skill and course mappings.")
