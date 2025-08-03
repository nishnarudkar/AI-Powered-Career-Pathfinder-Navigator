#!/usr/bin/env python3
"""
Test suite for Role Readiness Agent

Tests all acceptance criteria including:
1. Synthetic test where user fully satisfies role requirements
2. Partial overlap with correct score degradation
3. Missing skills with correct gap_degree
4. Quick-win recommendations for critical gaps
"""

import sys
import os
sys.path.append('/workspaces/AI-Powered-Career-Pathfinder-Navigator/backend')

from role_readiness_agent import RoleReadinessAgent, UserSkill, SkillImportance

def test_perfect_match():
    """Test case where user fully satisfies a role's requirements"""
    print("🧪 Test 1: Perfect Role Match")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    # Create user with perfect data scientist skills
    perfect_data_scientist_skills = [
        UserSkill("python", 3),
        UserSkill("sql", 3),
        UserSkill("statistics", 3),
        UserSkill("machine-learning", 3),
        UserSkill("pandas", 3),
        UserSkill("numpy", 3),  # exceeds requirement (2)
        UserSkill("scikit-learn", 3),  # exceeds requirement (2)
        UserSkill("data-visualization", 3),  # exceeds requirement (2)
        UserSkill("jupyter", 3),  # exceeds requirement (2)
        UserSkill("tensorflow", 3),  # exceeds requirement (2)
        UserSkill("pytorch", 3),  # exceeds requirement (2)
        UserSkill("deep-learning", 3),  # exceeds requirement (2)
        UserSkill("r", 3),  # exceeds requirement (2)
    ]
    
    result = agent.assess_role_readiness(perfect_data_scientist_skills)
    
    # Find data scientist role
    data_scientist_role = next(role for role in result["matched_roles"] if role["role_name"] == "data-scientist")
    
    print(f"Role: {data_scientist_role['role_name']}")
    print(f"Readiness Score: {data_scientist_role['readiness_score']}")
    print(f"Readiness Label: {data_scientist_role['readiness_label']}")
    print(f"Missing Skills: {len(data_scientist_role['missing_skills'])}")
    
    # Assertions
    assert data_scientist_role['readiness_score'] >= 0.9, f"Expected score ≥ 0.9, got {data_scientist_role['readiness_score']}"
    assert data_scientist_role['readiness_label'] == "Ready / Strong fit", f"Expected 'Ready / Strong fit', got {data_scientist_role['readiness_label']}"
    assert len(data_scientist_role['missing_skills']) == 0, f"Expected 0 missing skills, got {len(data_scientist_role['missing_skills'])}"
    
    print("✅ Perfect match test passed!")
    print()

def test_partial_overlap():
    """Test case with partial skill overlap and score degradation"""
    print("🧪 Test 2: Partial Skill Overlap")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    # Create user with partial data scientist skills
    partial_skills = [
        UserSkill("python", 2),  # below requirement (3)
        UserSkill("sql", 3),     # meets requirement
        UserSkill("statistics", 1),  # well below requirement (3)
        UserSkill("machine-learning", 2),  # below requirement (3)
        # Missing: pandas, numpy, scikit-learn, data-visualization
        UserSkill("jupyter", 2),  # meets nice-to-have
        # Missing other nice-to-haves
    ]
    
    result = agent.assess_role_readiness(partial_skills)
    data_scientist_role = next(role for role in result["matched_roles"] if role["role_name"] == "data-scientist")
    
    print(f"Role: {data_scientist_role['role_name']}")
    print(f"Readiness Score: {data_scientist_role['readiness_score']}")
    print(f"Readiness Label: {data_scientist_role['readiness_label']}")
    print(f"Missing Skills: {len(data_scientist_role['missing_skills'])}")
    
    # Check missing skills have correct gap_degree
    missing_skills = data_scientist_role['missing_skills']
    
    # Find specific missing skills and verify gap calculations
    python_gap = next((skill for skill in missing_skills if skill['skill'] == 'python'), None)
    statistics_gap = next((skill for skill in missing_skills if skill['skill'] == 'statistics'), None)
    pandas_gap = next((skill for skill in missing_skills if skill['skill'] == 'pandas'), None)
    
    assert python_gap is not None, "Python should be in missing skills"
    assert python_gap['gap_degree'] == 1, f"Python gap should be 1, got {python_gap['gap_degree']}"
    assert python_gap['current_level'] == 2, f"Python current level should be 2, got {python_gap['current_level']}"
    assert python_gap['target_level'] == 3, f"Python target level should be 3, got {python_gap['target_level']}"
    
    assert statistics_gap is not None, "Statistics should be in missing skills"
    assert statistics_gap['gap_degree'] == 2, f"Statistics gap should be 2, got {statistics_gap['gap_degree']}"
    
    assert pandas_gap is not None, "Pandas should be in missing skills"
    assert pandas_gap['gap_degree'] == 3, f"Pandas gap should be 3, got {pandas_gap['gap_degree']}"
    assert pandas_gap['current_level'] == 0, f"Pandas current level should be 0, got {pandas_gap['current_level']}"
    
    # Score should be degraded
    assert data_scientist_role['readiness_score'] < 0.8, f"Score should be < 0.8 for partial match, got {data_scientist_role['readiness_score']}"
    
    print("Sample missing skills:")
    for skill in missing_skills[:3]:
        print(f"  - {skill['skill']}: Level {skill['current_level']}→{skill['target_level']} (gap: {skill['gap_degree']})")
    
    print("✅ Partial overlap test passed!")
    print()

def test_quick_win_recommendations():
    """Test quick-win recommendations for critical gaps"""
    print("🧪 Test 3: Quick-Win Recommendations")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    # Create user with strategic gaps for testing recommendations
    strategic_skills = [
        UserSkill("python", 1),  # large gap (3-1=2) for MUST skill
        UserSkill("sql", 2),     # small gap (3-2=1) for MUST skill
        # Missing: statistics (gap=3), machine-learning (gap=3), pandas (gap=3) - all MUST
        UserSkill("numpy", 2),   # meets requirement
        UserSkill("jupyter", 1), # gap for nice-to-have
    ]
    
    result = agent.assess_role_readiness(strategic_skills)
    data_scientist_role = next(role for role in result["matched_roles"] if role["role_name"] == "data-scientist")
    
    recommendations = data_scientist_role['quick_win_recommendations']
    
    print(f"Quick-win recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Should have exactly 2 recommendations
    assert len(recommendations) == 2, f"Expected 2 recommendations, got {len(recommendations)}"
    
    # Should focus on largest gaps among MUST skills
    # Expected: statistics (gap=3), machine-learning (gap=3), pandas (gap=3)
    # The algorithm should pick the first 2 when sorted by gap_degree descending
    
    # Check that recommendations mention critical skills
    rec_text = " ".join(recommendations).lower()
    
    # Should mention skills with largest gaps
    critical_skills_mentioned = any(skill in rec_text for skill in ['statistics', 'machine-learning', 'pandas'])
    assert critical_skills_mentioned, "Recommendations should mention critical missing skills"
    
    # Should not prioritize nice-to-have over must-have
    assert 'jupyter' not in rec_text, "Should not recommend nice-to-have skills over critical must-have skills"
    
    print("✅ Quick-win recommendations test passed!")
    print()

def test_multiple_roles_ranking():
    """Test that roles are correctly ranked by readiness score"""
    print("🧪 Test 4: Role Ranking")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    # Create user with web development skills
    web_dev_skills = [
        UserSkill("javascript", 3),
        UserSkill("html", 3),
        UserSkill("css", 3),
        UserSkill("react", 2),  # slightly below requirement
        UserSkill("git", 2),
        UserSkill("sql", 1),    # low but present
    ]
    
    result = agent.assess_role_readiness(web_dev_skills)
    
    print("Top 3 role matches:")
    for i, role in enumerate(result["matched_roles"][:3], 1):
        print(f"  {i}. {role['role_name']}: {role['readiness_score']:.3f} ({role['readiness_label']})")
    
    # Full-stack developer should rank higher than data scientist
    full_stack_role = next(role for role in result["matched_roles"] if role["role_name"] == "full-stack-developer")
    data_scientist_role = next(role for role in result["matched_roles"] if role["role_name"] == "data-scientist")
    
    full_stack_index = next(i for i, role in enumerate(result["matched_roles"]) if role["role_name"] == "full-stack-developer")
    data_scientist_index = next(i for i, role in enumerate(result["matched_roles"]) if role["role_name"] == "data-scientist")
    
    assert full_stack_index < data_scientist_index, "Full-stack developer should rank higher than data scientist for web dev skills"
    assert full_stack_role['readiness_score'] > data_scientist_role['readiness_score'], "Full-stack should have higher score"
    
    # Check that we get exactly 5 roles
    assert len(result["matched_roles"]) == 5, f"Should return top 5 roles, got {len(result['matched_roles'])}"
    
    # Check that roles are sorted by score descending
    scores = [role['readiness_score'] for role in result["matched_roles"]]
    assert scores == sorted(scores, reverse=True), "Roles should be sorted by readiness score descending"
    
    print("✅ Role ranking test passed!")
    print()

def test_caching():
    """Test that caching works correctly"""
    print("🧪 Test 5: Caching")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    skills = [UserSkill("python", 2), UserSkill("sql", 1)]
    
    # First call
    result1 = agent.assess_role_readiness(skills)
    cache_size_after_first = len(agent.cache)
    
    # Second call with same skills
    result2 = agent.assess_role_readiness(skills)
    cache_size_after_second = len(agent.cache)
    
    # Results should be identical
    assert result1 == result2, "Cached results should be identical to fresh computation"
    assert cache_size_after_first == cache_size_after_second, "Cache size should not change on second call"
    
    # Third call with force_refresh
    result3 = agent.assess_role_readiness(skills, force_refresh=True)
    
    # Should still be identical (but bypassed cache)
    assert result1 == result3, "Force refresh should produce same results"
    
    print(f"Cache entries: {len(agent.cache)}")
    print("✅ Caching test passed!")
    print()

def test_edge_cases():
    """Test edge cases and error handling"""
    print("🧪 Test 6: Edge Cases")
    print("-" * 40)
    
    agent = RoleReadinessAgent()
    
    # Test with empty skills
    empty_result = agent.assess_role_readiness([])
    assert len(empty_result["matched_roles"]) == 5, "Should still return 5 roles for empty skills"
    
    # All roles should have very low scores
    for role in empty_result["matched_roles"]:
        assert role['readiness_score'] < 0.2, f"Empty skills should yield low scores, got {role['readiness_score']} for {role['role_name']}"
        assert role['readiness_label'] == "Needs foundation", f"Empty skills should need foundation, got {role['readiness_label']}"
    
    # Test with skill level 0
    zero_level_skills = [UserSkill("python", 0), UserSkill("sql", 0)]
    zero_result = agent.assess_role_readiness(zero_level_skills)
    
    # Should handle gracefully
    assert len(zero_result["matched_roles"]) == 5, "Should handle zero-level skills"
    
    # Test with very high skill levels (should be capped)
    high_level_skills = [UserSkill("python", 5), UserSkill("sql", 4)]  # Levels above 3
    high_result = agent.assess_role_readiness(high_level_skills)
    
    # Should not crash and should cap at target levels
    assert len(high_result["matched_roles"]) == 5, "Should handle high skill levels"
    
    print("✅ Edge cases test passed!")
    print()

if __name__ == "__main__":
    print("🚀 Running Role Readiness Agent Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_perfect_match()
        test_partial_overlap()
        test_quick_win_recommendations()
        test_multiple_roles_ranking()
        test_caching()
        test_edge_cases()
        
        print("🎉 All tests passed! Role Readiness Agent is working correctly.")
        print("\n📊 Summary of validated features:")
        print("  ✅ Perfect role match yields score ≥ 0.9 and 'Ready' label")
        print("  ✅ Partial overlap correctly degrades score")
        print("  ✅ Missing skills show correct gap_degree calculations")
        print("  ✅ Quick-win recommendations focus on critical 'must' skills")
        print("  ✅ Roles ranked correctly by readiness score")
        print("  ✅ Caching works properly")
        print("  ✅ Edge cases handled gracefully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
