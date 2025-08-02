#!/usr/bin/env python3
"""
Calculate and display input lengths for all sample resume files.
This script shows how the character counts are calculated.
"""

import os
import glob

def calculate_input_lengths():
    """Calculate and display input lengths for sample resume files"""
    
    print("📊 Sample Resume Input Length Calculator")
    print("=" * 50)
    
    # Get all sample resume files
    sample_files = glob.glob("sample_resume_*.txt")
    sample_files.sort()
    
    if not sample_files:
        print("❌ No sample resume files found!")
        print("Make sure you're running this from the sample_data directory.")
        return
    
    total_chars = 0
    file_data = []
    
    for filename in sample_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                char_count = len(content)
                total_chars += char_count
                
                # Extract resume type from filename
                resume_type = filename.replace('sample_resume_', '').replace('.txt', '').replace('_', ' ').title()
                
                file_data.append({
                    'filename': filename,
                    'type': resume_type,
                    'length': char_count,
                    'content_preview': content[:100] + "..." if len(content) > 100 else content
                })
                
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
    
    # Display results
    print(f"\n📋 Resume Sample Analysis ({len(file_data)} files)")
    print("-" * 50)
    
    for i, data in enumerate(file_data, 1):
        print(f"{i}. {data['type']}")
        print(f"   📁 File: {data['filename']}")
        print(f"   📏 Length: {data['length']} characters")
        print(f"   📝 Preview: {data['content_preview']}")
        print()
    
    # Summary statistics
    lengths = [data['length'] for data in file_data]
    min_length = min(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    
    print("📊 SUMMARY STATISTICS")
    print("-" * 50)
    print(f"📁 Total Files: {len(file_data)}")
    print(f"📏 Total Characters: {total_chars:,}")
    print(f"📉 Shortest Resume: {min_length} chars")
    print(f"📈 Longest Resume: {max_length} chars")
    print(f"📊 Average Length: {avg_length:.1f} chars")
    
    # Length categorization
    short_resumes = [d for d in file_data if d['length'] < 300]
    medium_resumes = [d for d in file_data if 300 <= d['length'] < 700]
    long_resumes = [d for d in file_data if d['length'] >= 700]
    
    print(f"\n📂 LENGTH CATEGORIES")
    print("-" * 50)
    print(f"📝 Short (<300 chars): {len(short_resumes)} files")
    for resume in short_resumes:
        print(f"   • {resume['type']}: {resume['length']} chars")
    
    print(f"\n📄 Medium (300-699 chars): {len(medium_resumes)} files")
    for resume in medium_resumes:
        print(f"   • {resume['type']}: {resume['length']} chars")
    
    print(f"\n📑 Long (700+ chars): {len(long_resumes)} files")
    for resume in long_resumes:
        print(f"   • {resume['type']}: {resume['length']} chars")
    
    # Show how length calculation works
    print(f"\n🔧 HOW LENGTH IS CALCULATED")
    print("-" * 50)
    print("The input length is calculated using Python's len() function:")
    print()
    print("```python")
    print("with open('resume.txt', 'r') as f:")
    print("    content = f.read()")
    print("    input_length = len(content)  # Counts all characters")
    print("```")
    print()
    print("This includes:")
    print("✅ Letters and numbers")
    print("✅ Spaces and tabs")  
    print("✅ Newlines (\\n)")
    print("✅ Special characters (•, -, :, etc.)")
    print("✅ Punctuation marks")
    
    return file_data

if __name__ == "__main__":
    # Change to sample_data directory if not already there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    calculate_input_lengths()
