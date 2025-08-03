#!/usr/bin/env python3
"""
Test script for role readiness summary generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from role_readiness_agent import RoleReadinessAgent

def test_role_summary_generation():
    """Test the role summary generation functionality"""
    
    print("🧪 Testing Role Summary Generation")
    print("=" * 50)
    
    # Create agent
    agent = RoleReadinessAgent()
    
    # Test skills for a data science candidate
    test_skills = [
        "python", "sql", "machine-learning", "pandas", "numpy", 
        "scikit-learn", "jupyter", "git", "statistics"
    ]
    
    # Get role assessment
    assessment = agent.assess_from_raw_skills(test_skills)
    
    print(f"Test Skills: {', '.join(test_skills)}")
    print()
    
    # Generate summaries for each role
    for role_match in assessment.get('matched_roles', []):
        role_name = role_match['role_name']
        summary = agent.generate_role_summary(role_match)
        
        print(f"Role: {role_name}")
        print(f"Summary: {summary}")
        print(f"Word count: {len(summary.split())} words")
        print("-" * 40)
    
    print("\n✅ Summary generation test completed!")

def test_edge_cases():
    """Test edge cases for summary generation"""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 30)
    
    agent = RoleReadinessAgent()
    
    # Test with minimal skills
    minimal_skills = ["html", "css"]
    assessment = agent.assess_from_raw_skills(minimal_skills)
    
    print("Minimal Skills Test:")
    for role_match in assessment.get('matched_roles', [])[:2]:  # Just first 2
        summary = agent.generate_role_summary(role_match)
        print(f"- {role_match['role_name']}: {summary}")
    
    # Test with many skills
    extensive_skills = [
        "python", "javascript", "react", "node.js", "sql", "mongodb",
        "docker", "kubernetes", "aws", "machine-learning", "tensorflow",
        "git", "jenkins", "linux", "api-design", "microservices"
    ]
    assessment = agent.assess_from_raw_skills(extensive_skills)
    
    print("\nExtensive Skills Test:")
    for role_match in assessment.get('matched_roles', [])[:2]:  # Just first 2
        summary = agent.generate_role_summary(role_match)
        print(f"- {role_match['role_name']}: {summary}")

if __name__ == "__main__":
    test_role_summary_generation()
    test_edge_cases()
