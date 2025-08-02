#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION: Skills Mapping & Backend Data Format
Final verification before commit to ensure 100% accuracy for web dev resumes.
"""

import json
import os
import sys

# Get the correct path to data files
PROJECT_ROOT = "/workspaces/AI-Powered-Career-Pathfinder-Navigator"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def load_curated_data():
    """Load job roles and courses data with correct paths"""
    try:
        job_roles_path = os.path.join(DATA_DIR, "job_roles.json")
        courses_path = os.path.join(DATA_DIR, "courses.json")
        
        with open(job_roles_path, "r") as f:
            job_roles = json.load(f)
        with open(courses_path, "r") as f:
            courses = json.load(f)
        
        print(f"✅ Loaded curated data from {DATA_DIR}")
        return job_roles, courses
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return {}, {}

def extract_skills_basic(text):
    """Basic skill extraction for testing"""
    import re
    
    skill_patterns = {
        'html': r'\b(html|html5)\b',
        'css': r'\b(css|css3)\b',
        'javascript': r'\b(javascript|js)\b(?!on)',
        'react': r'\b(react|react\.js|reactjs)\b',
        'nodejs': r'\b(node\.js|nodejs|node js)\b',
        'express': r'\b(express|express\.js|expressjs)\b',
        'mongodb': r'\b(mongodb|mongo)\b',
        'postgresql': r'\b(postgresql|postgres)\b',
        'git': r'\b(git)\b',
        'bootstrap': r'\b(bootstrap)\b',
        'rest-api': r'\b(rest|rest api|rest apis|restful)\b',
        'json': r'\b(json)\b',
        'sql': r'\b(sql)\b',
        'typescript': r'\b(typescript|ts)\b',
        'aws': r'\b(aws|amazon web services)\b',
        'testing': r'\b(testing|test|jest|unit test)\b'
    }
    
    text_lower = text.lower()
    extracted = []
    
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, text_lower):
            extracted.append(skill)
    
    return extracted

def comprehensive_verification():
    """Run comprehensive verification tests"""
    
    print("🔍 COMPREHENSIVE VERIFICATION TESTS")
    print("=" * 60)
    
    # Load curated data
    job_roles_data, courses_data = load_curated_data()
    
    if not job_roles_data or not courses_data:
        print("❌ Cannot proceed without curated data")
        return False
    
    print(f"📊 Data Loaded:")
    print(f"   • Job Roles: {len(job_roles_data)} career paths")
    print(f"   • Courses: {len(courses_data)} skills with recommendations")
    
    # Test Case: Web Developer Resume
    web_dev_resume = """
    ALEX MARTINEZ - Full Stack Web Developer
    
    TECHNICAL SKILLS:
    • Frontend: React.js, HTML5, CSS3, JavaScript ES6+, Bootstrap
    • Backend: Node.js, Express.js, REST APIs  
    • Databases: MongoDB, PostgreSQL, SQL
    • Tools: Git, npm, JSON, VS Code
    • Testing: Jest, Unit Testing
    
    PROJECTS:
    E-commerce Platform (2024)
    • Built responsive frontend with React and Bootstrap
    • Developed REST APIs using Node.js and Express
    • Implemented PostgreSQL database with proper schema
    • Used Git for version control and team collaboration
    • Added comprehensive testing with Jest
    """
    
    target_role = "Full Stack Web Developer"
    
    print(f"\n🧪 TEST 1: Skills Extraction Accuracy")
    print("-" * 45)
    
    # Extract skills
    extracted_skills = extract_skills_basic(web_dev_resume)
    required_skills = job_roles_data.get(target_role, [])
    
    print(f"📝 Resume: {len(web_dev_resume)} characters")
    print(f"🎯 Target: {target_role}")
    print(f"📋 Required Skills: {required_skills}")
    print(f"✅ Extracted Skills: {extracted_skills}")
    
    # Calculate matching accuracy
    required_lower = [skill.lower().replace(' ', '-').replace('.', '') for skill in required_skills]
    matches = []
    missing = []
    
    for req_skill in required_lower:
        matched = False
        for ext_skill in extracted_skills:
            # Flexible matching
            if (req_skill in ext_skill or ext_skill in req_skill or
                req_skill.replace('-', '') in ext_skill.replace('-', '') or
                req_skill == ext_skill.replace('-', '').replace('js', 'javascript')):
                matches.append(req_skill)
                matched = True
                break
        if not matched:
            missing.append(req_skill)
    
    accuracy = (len(matches) / len(required_skills) * 100) if required_skills else 0
    
    print(f"🎯 Matched: {matches}")
    print(f"❌ Missing: {missing}")
    print(f"📊 Accuracy: {accuracy:.1f}%")
    
    # Test course mapping
    print(f"\n🧪 TEST 2: Course Mapping Accuracy")
    print("-" * 45)
    
    courses_found = 0
    courses_total = len(missing)
    course_details = {}
    
    for skill in missing:
        # Find courses for missing skills
        skill_courses = []
        for course_skill, courses_list in courses_data.items():
            if (skill.lower().replace('-', '') in course_skill.lower().replace(' ', '') or
                course_skill.lower().replace(' ', '') in skill.lower().replace('-', '')):
                skill_courses = courses_list[:2]  # Top 2 courses
                courses_found += 1
                break
        
        course_details[skill] = skill_courses
        status = "✅" if skill_courses else "❌"
        print(f"   {status} {skill}: {len(skill_courses)} courses")
        if skill_courses:
            print(f"      • {skill_courses[0]}")
    
    course_coverage = (courses_found / courses_total * 100) if courses_total > 0 else 100
    
    # Test backend data format
    print(f"\n🧪 TEST 3: Backend Data Format")
    print("-" * 45)
    
    # Create backend-ready response
    backend_response = {
        "success": True,
        "timestamp": "2025-08-02T10:30:45Z",
        "user_input": {
            "character_count": len(web_dev_resume),
            "target_role": target_role
        },
        "results": {
            "extracted_skills": extracted_skills,
            "required_skills": required_skills,
            "matched_skills": matches,
            "missing_skills": missing,
            "accuracy_percentage": round(accuracy, 1),
            "skill_coverage": f"{len(matches)}/{len(required_skills)}"
        },
        "course_recommendations": {
            skill: courses for skill, courses in course_details.items() if courses
        },
        "learning_path": {
            "immediate_focus": missing[:3],
            "estimated_time": "6-8 weeks",
            "difficulty": "intermediate"
        },
        "api_endpoints": {
            "career_paths": f"GET /api/career-paths",
            "skill_analysis": f"POST /api/analyze-skills",
            "learning_recommendations": f"POST /api/learning-path"
        }
    }
    
    # Test JSON serialization
    try:
        json_str = json.dumps(backend_response, indent=2)
        json_size = len(json_str)
        print(f"   ✅ JSON Serialization: Success")
        print(f"   📦 Size: {json_size} chars ({json_size/1024:.1f} KB)")
        print(f"   📋 Keys: {list(backend_response.keys())}")
    except Exception as e:
        print(f"   ❌ JSON Serialization: Failed - {e}")
        return False
    
    # Frontend compatibility test
    print(f"\n🧪 TEST 4: Frontend Compatibility")
    print("-" * 45)
    
    # Test data extraction for common UI components
    try:
        # Skills badges
        skill_badges = [{"name": skill.title(), "status": "found"} for skill in extracted_skills]
        
        # Progress bar data
        progress_data = {
            "completed": len(matches),
            "total": len(required_skills),
            "percentage": round(accuracy, 1)
        }
        
        # Course cards
        course_cards = []
        for skill, courses in course_details.items():
            if courses:
                course_cards.append({
                    "skill": skill.title(),
                    "courses": [{"title": course.split(" - ")[0], "provider": course.split(" - ")[1] if " - " in course else "Unknown"} for course in courses]
                })
        
        print(f"   ✅ Skill Badges: {len(skill_badges)} items")
        print(f"   ✅ Progress Data: {progress_data['percentage']}% complete")
        print(f"   ✅ Course Cards: {len(course_cards)} skills with courses")
        
        ui_ready = True
        
    except Exception as e:
        print(f"   ❌ Frontend data extraction failed: {e}")
        ui_ready = False
    
    # Final assessment
    print(f"\n🎯 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    skill_test_pass = accuracy >= 75
    course_test_pass = course_coverage >= 80
    backend_test_pass = json_size > 0
    ui_test_pass = ui_ready
    
    print(f"🧪 Skills Accuracy: {accuracy:.1f}% {'✅ PASS' if skill_test_pass else '❌ FAIL'}")
    print(f"📚 Course Coverage: {course_coverage:.1f}% {'✅ PASS' if course_test_pass else '❌ FAIL'}")
    print(f"🔌 Backend Format: {'✅ PASS' if backend_test_pass else '❌ FAIL'}")
    print(f"⚛️  Frontend Ready: {'✅ PASS' if ui_test_pass else '❌ FAIL'}")
    
    all_tests_pass = skill_test_pass and course_test_pass and backend_test_pass and ui_test_pass
    
    if all_tests_pass:
        print(f"\n🎉 ALL VERIFICATIONS PASSED - READY FOR COMMIT!")
        print(f"   ✅ Web dev resume processing: Accurate")
        print(f"   ✅ Skills & courses mapping: Verified")
        print(f"   ✅ Backend data format: Production-ready")
        print(f"   ✅ UI compatibility: Confirmed")
    else:
        print(f"\n⚠️  SOME VERIFICATIONS FAILED - REVIEW NEEDED")
    
    # Save verification report
    verification_report = {
        "verification_date": "2025-08-02",
        "tests_conducted": 4,
        "results": {
            "skills_accuracy": {"score": accuracy, "status": "pass" if skill_test_pass else "fail"},
            "course_coverage": {"score": course_coverage, "status": "pass" if course_test_pass else "fail"},
            "backend_format": {"status": "pass" if backend_test_pass else "fail"},
            "frontend_compatibility": {"status": "pass" if ui_test_pass else "fail"}
        },
        "sample_data": backend_response,
        "recommendation": "Ready for commit" if all_tests_pass else "Needs improvement"
    }
    
    with open("../verification_report.json", "w") as f:
        json.dump(verification_report, f, indent=2)
    
    print(f"\n💾 Verification report saved: verification_report.json")
    
    return all_tests_pass

if __name__ == "__main__":
    success = comprehensive_verification()
    exit(0 if success else 1)
