# Sample Resume/CV Data for Agent 1 Testing

This directory contains sample resume and CV data used for testing Agent 1's skill extraction capabilities.

## Files Overview

- `sample_resume_1_data_scientist.txt` - Senior Data Scientist resume (1,156 characters)
- `sample_resume_2_full_stack.txt` - Full Stack Developer resume (1,000 characters) 
- `sample_resume_3_junior_dev.txt` - Junior Developer resume (453 characters)
- `sample_resume_4_traditional.txt` - Traditional resume format (688 characters)
- `sample_resume_5_bullet_point.txt` - Bullet point format (371 characters)
- `sample_resume_6_narrative.txt` - Narrative CV style (578 characters)
- `sample_resume_7_project_based.txt` - Project-based format (516 characters)
- `sample_resume_8_minimal.txt` - Minimal skills list (106 characters)
- `sample_resume_9_complex.txt` - Complex resume with variations (628 characters)

## Usage

These samples are used to test:
- Different resume formats and structures
- Skill extraction accuracy across experience levels
- Agent 1's fallback mechanism performance
- Integration with Agent 2 for gap analysis

## Character Count Calculation

The input length is calculated using Python's `len()` function:
```python
input_length = len(resume_text)
```

This counts all characters including spaces, newlines, and special characters in the resume text.
