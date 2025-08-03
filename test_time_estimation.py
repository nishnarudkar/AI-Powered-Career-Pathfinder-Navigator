#!/usr/bin/env python3
"""
Test script to verify time estimation functionality
"""

import sys
import os
sys.path.append('/workspaces/AI-Powered-Career-Pathfinder-Navigator/backend')

from career_pathfinder_optimized import calculate_time_estimates, estimate_skill_hours

def test_skill_hour_estimation():
    """Test individual skill hour estimation"""
    print("🧪 Testing skill hour estimation...")
    
    test_skills = [
        ("python", 15),  # Programming language
        ("javascript", 15),  # Programming language
        ("sql", 12),  # Database
        ("git", 6),  # Tool
        ("machine-learning", 18),  # Data science
        ("html", 8),  # Web technology
        ("aws", 10),  # Cloud platform
        ("unknown-skill", 10)  # Default
    ]
    
    for skill, expected in test_skills:
        estimated = estimate_skill_hours(skill)
        print(f"  {skill}: {estimated}h (expected: {expected}h)")
        assert estimated == expected, f"Expected {expected}h for {skill}, got {estimated}h"
    
    print("✅ Skill hour estimation tests passed!")

def test_time_estimates_calculation():
    """Test phase and overall time calculation"""
    print("\n🧪 Testing time estimates calculation...")
    
    # Sample roadmap data
    sample_roadmap = [
        {
            "phase": "Phase 1: Foundation",
            "skills": [
                {"skill": "python", "course": "Python Course", "reason": "Foundation", "est_hours": 15},
                {"skill": "git", "course": "Git Course", "reason": "Version control", "est_hours": 6},
                {"skill": "sql", "course": "SQL Course", "reason": "Database basics", "est_hours": 12}
            ]
        },
        {
            "phase": "Phase 2: Advanced",
            "skills": [
                {"skill": "machine-learning", "course": "ML Course", "reason": "Advanced skills", "est_hours": 18},
                {"skill": "aws", "course": "AWS Course", "reason": "Cloud skills", "est_hours": 10}
            ]
        }
    ]
    
    # Test with default weekly hours (8)
    result = calculate_time_estimates(sample_roadmap, weekly_hours=8)
    
    print(f"  Overall total hours: {result['overall_total_hours']}")
    print(f"  Overall buffered hours: {result['overall_buffered_hours']}")
    print(f"  Weekly hours: {result['weekly_hours']}")
    print(f"  Overall time frame: {result['overall_time_frame']}")
    
    # Expected calculations:
    # Phase 1: 15 + 6 + 12 = 33 hours
    # Phase 2: 18 + 10 = 28 hours
    # Total: 33 + 28 = 61 hours
    # Buffered: 61 * 1.1 = 67 hours
    
    assert result['overall_total_hours'] == 61, f"Expected 61 total hours, got {result['overall_total_hours']}"
    assert result['overall_buffered_hours'] == 67, f"Expected 67 buffered hours, got {result['overall_buffered_hours']}"
    assert result['weekly_hours'] == 8, f"Expected 8 weekly hours, got {result['weekly_hours']}"
    
    # Check phase calculations
    phases = result['phases']
    assert len(phases) == 2, f"Expected 2 phases, got {len(phases)}"
    
    phase1 = phases[0]
    assert phase1['phase_total_hours'] == 33, f"Expected 33 hours for phase 1, got {phase1['phase_total_hours']}"
    assert "33 hours (~5 weeks at 8 hrs/week)" in phase1['phase_time_frame']
    
    phase2 = phases[1] 
    assert phase2['phase_total_hours'] == 28, f"Expected 28 hours for phase 2, got {phase2['phase_total_hours']}"
    assert "28 hours (~4 weeks at 8 hrs/week)" in phase2['phase_time_frame']
    
    print("✅ Time estimates calculation tests passed!")

def test_missing_est_hours():
    """Test handling of missing est_hours in skills"""
    print("\n🧪 Testing missing est_hours handling...")
    
    # Sample roadmap without est_hours
    sample_roadmap = [
        {
            "phase": "Phase 1: Foundation",
            "skills": [
                {"skill": "python", "course": "Python Course", "reason": "Foundation"},  # No est_hours
                {"skill": "javascript", "course": "JS Course", "reason": "Frontend"}     # No est_hours
            ]
        }
    ]
    
    result = calculate_time_estimates(sample_roadmap, weekly_hours=10)
    
    # Should auto-assign hours: python=15, javascript=15, total=30
    assert result['overall_total_hours'] == 30, f"Expected 30 total hours, got {result['overall_total_hours']}"
    
    # Check that est_hours were added to skills
    skills = result['phases'][0]['skills']
    assert skills[0]['est_hours'] == 15, f"Expected python to have 15 hours, got {skills[0].get('est_hours')}"
    assert skills[1]['est_hours'] == 15, f"Expected javascript to have 15 hours, got {skills[1].get('est_hours')}"
    
    print("✅ Missing est_hours handling tests passed!")

def test_custom_weekly_hours():
    """Test custom weekly hours settings"""
    print("\n🧪 Testing custom weekly hours...")
    
    sample_roadmap = [
        {
            "phase": "Phase 1: Foundation", 
            "skills": [
                {"skill": "python", "course": "Python Course", "reason": "Foundation", "est_hours": 20}
            ]
        }
    ]
    
    # Test with 5 hours per week
    result = calculate_time_estimates(sample_roadmap, weekly_hours=5)
    
    assert result['weekly_hours'] == 5, f"Expected 5 weekly hours, got {result['weekly_hours']}"
    # 20 hours / 5 hours per week = 4 weeks
    assert "4 weeks at 5 hrs/week" in result['phases'][0]['phase_time_frame']
    
    print("✅ Custom weekly hours tests passed!")

if __name__ == "__main__":
    print("🚀 Running time estimation tests...\n")
    
    try:
        test_skill_hour_estimation()
        test_time_estimates_calculation()
        test_missing_est_hours()
        test_custom_weekly_hours()
        
        print("\n🎉 All tests passed! Time estimation functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
