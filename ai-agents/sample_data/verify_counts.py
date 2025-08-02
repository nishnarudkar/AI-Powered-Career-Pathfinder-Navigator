#!/usr/bin/env python3
"""
Verify character counts for sample data
"""

# Main pipeline input from career_pathfinder_langgraph.py
main_pipeline_input = """
    Software Engineer with 3 years experience
    Skills: Python, JavaScript, React, Node.js, MongoDB, Git
    Experience: Built web applications, REST APIs, worked with databases
    Education: Computer Science degree
    """

print("🔍 Character Count Verification")
print("=" * 40)
print(f"Main pipeline input: {len(main_pipeline_input)} characters")
print(f"Content: {repr(main_pipeline_input)}")

# Clean version without indentation
clean_input = """Software Engineer with 3 years experience
Skills: Python, JavaScript, React, Node.js, MongoDB, Git
Experience: Built web applications, REST APIs, worked with databases
Education: Computer Science degree"""

print(f"\nClean version: {len(clean_input)} characters")
print(f"Content: {repr(clean_input)}")

# Show breakdown
lines = clean_input.split('\n')
print(f"\nLine breakdown:")
total = 0
for i, line in enumerate(lines, 1):
    length = len(line)
    total += length
    print(f"Line {i}: {length} chars - '{line}'")

print(f"\nTotal characters in lines: {total}")
print(f"Plus newlines ({len(lines)-1}): {len(lines)-1}")
print(f"Total with newlines: {total + len(lines) - 1}")
print(f"Using len() function: {len(clean_input)}")
