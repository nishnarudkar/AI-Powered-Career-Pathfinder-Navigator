#!/usr/bin/env python3
"""
Agent 1 Mock Test - Test the enhanced fallback extraction function
Directly tests the extract_skills_fallback function we implemented.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fallback function from our updated file
from career_pathfinder_langgraph import extract_skills_fallback

def test_enhanced_agent1():
    """Test the enhanced Agent 1 fallback function"""
    
    print("🔧 Agent 1 Enhanced Fallback Test")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Complex Resume with Variations",
            "input": """
            SENIOR SOFTWARE ENGINEER
            
            Technical Skills:
            • Programming Languages: Python, JavaScript (ES6+), TypeScript, Java
            • Frontend: React.js, Vue.js, HTML5, CSS3, Bootstrap
            • Backend: Node.js, Express.js, Django, Flask
            • Databases: PostgreSQL, MongoDB, MySQL, Redis, SQLite
            • Cloud: AWS (EC2, S3, Lambda), Google Cloud Platform, Azure
            • DevOps: Docker, Kubernetes, Git, CI/CD, Jenkins
            • Data Science: Pandas, NumPy, Scikit-Learn, TensorFlow
            • Tools: Jupyter Notebooks, Tableau, Figma, Jira
            """,
            "expected_min": 20
        },
        {
            "name": "Project Description Format",
            "input": """
            PROJECT: E-commerce Platform
            Built a full-stack e-commerce platform using:
            - React for the frontend with TypeScript
            - Node.js and Express for the backend APIs
            - PostgreSQL database with Prisma ORM
            - Deployed on AWS using Docker containers
            - Used Git for version control
            - Implemented payment processing with Stripe
            """,
            "expected_min": 8
        },
        {
            "name": "Narrative CV Style",
            "input": """
            I am a data scientist with 5 years of experience in machine learning 
            and statistical analysis. I primarily code in Python and R programming 
            language. My expertise includes working with Pandas for data manipulation, 
            NumPy for numerical computing, and Scikit-Learn for machine learning models. 
            I have experience with TensorFlow and PyTorch for deep learning projects. 
            I use Jupyter notebooks for analysis and create visualizations with Tableau 
            and matplotlib. I'm proficient in SQL for database queries and have worked 
            with both PostgreSQL and MongoDB databases.
            """,
            "expected_min": 12
        },
        {
            "name": "Minimal Skills List",
            "input": """
            Skills: HTML, CSS, JavaScript, React, Node.js, Git
            Experience: 2 years web development
            """,
            "expected_min": 6
        }
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Run the fallback extraction
        extracted_skills = extract_skills_fallback(test_case['input'])
        expected_min = test_case['expected_min']
        
        print(f"📝 Input length: {len(test_case['input'])} characters")
        print(f"✅ Extracted skills: {len(extracted_skills)}")
        print(f"🎯 Expected minimum: {expected_min}")
        print(f"📋 Skills found: {extracted_skills}")
        
        # Check if we met the minimum threshold
        if len(extracted_skills) >= expected_min:
            passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"🏆 Status: {status}")
        
        # Show skill categorization
        prog_languages = [s for s in extracted_skills if s in ['python', 'javascript', 'java', 'typescript', 'csharp', 'cpp']]
        frameworks = [s for s in extracted_skills if s in ['react', 'vuejs', 'angular', 'django', 'flask', 'express']]
        databases = [s for s in extracted_skills if s in ['postgresql', 'mongodb', 'mysql', 'sqlite', 'redis']]
        tools = [s for s in extracted_skills if s in ['git', 'docker', 'kubernetes', 'jupyter', 'tableau']]
        
        if prog_languages or frameworks or databases or tools:
            print(f"   📊 Categorization:")
            if prog_languages: print(f"      Languages: {prog_languages}")
            if frameworks: print(f"      Frameworks: {frameworks}")
            if databases: print(f"      Databases: {databases}")
            if tools: print(f"      Tools: {tools}")
    
    # Overall results
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 OVERALL RESULTS")
    print("=" * 50)
    print(f"🎯 Total Tests: {total_tests}")
    print(f"✅ Passed Tests: {passed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        overall_status = "✅ EXCELLENT"
        recommendation = "Agent 1 fallback mechanism is robust and ready for production!"
    elif success_rate >= 60:
        overall_status = "⚠️  GOOD"
        recommendation = "Agent 1 fallback works well but could benefit from minor improvements."
    else:
        overall_status = "❌ NEEDS IMPROVEMENT"
        recommendation = "Agent 1 fallback needs significant enhancement."
    
    print(f"\n🎯 Overall Assessment: {overall_status}")
    print(f"💡 Recommendation: {recommendation}")
    
    # Test skill normalization
    print(f"\n🔧 SKILL NORMALIZATION TEST")
    print("=" * 50)
    test_variations = [
        "React.js should become 'react'",
        "Node.js should become 'nodejs'", 
        "JavaScript should become 'javascript'",
        "PostgreSQL should become 'postgresql'",
        "Scikit-Learn should become 'scikit-learn'"
    ]
    
    normalization_input = "I use React.js, Node.js, JavaScript, PostgreSQL, and Scikit-Learn"
    normalized_skills = extract_skills_fallback(normalization_input)
    
    print(f"📝 Input: {normalization_input}")
    print(f"✅ Normalized output: {normalized_skills}")
    
    expected_normalized = ['react', 'nodejs', 'javascript', 'postgresql', 'scikit-learn']
    found_normalized = [skill for skill in expected_normalized if skill in normalized_skills]
    normalization_accuracy = (len(found_normalized) / len(expected_normalized)) * 100
    
    print(f"🎯 Normalization accuracy: {normalization_accuracy:.1f}%")
    
    if normalization_accuracy >= 80:
        print("✅ Skill normalization works excellently!")
    else:
        print("⚠️  Skill normalization needs improvement.")
    
    return success_rate >= 80

if __name__ == "__main__":
    test_enhanced_agent1()
