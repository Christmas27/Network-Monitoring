#!/usr/bin/env python3
"""
File Structure Analysis - Identify Legacy vs Current Files
"""

import os
import json
from pathlib import Path

def analyze_project_structure():
    """Analyze current project structure and categorize files"""
    
    # Define file categories
    categories = {
        "streamlit_app": {
            "description": "Current Streamlit Application Files",
            "files": [],
            "patterns": ["streamlit_app*.py", "app_pages/", "components/", "utils/"]
        },
        "legacy_flask": {
            "description": "Legacy Flask Application Files",
            "files": [],
            "patterns": ["main.py", "templates/", "static/", "*.html", "*.css", "*.js"]
        },
        "backend_modules": {
            "description": "Backend Modules (Keep)",
            "files": [],
            "patterns": ["modules/", "config/"]
        },
        "data_files": {
            "description": "Data and Configuration Files (Keep)",
            "files": [],
            "patterns": ["data/", "ansible_playbooks/", "*.yml", "*.yaml", "*.json"]
        },
        "documentation": {
            "description": "Documentation Files (Keep)",
            "files": [],
            "patterns": ["*.md", "docs/", "README*"]
        },
        "deployment": {
            "description": "Deployment Files (Keep)",
            "files": [],
            "patterns": ["Dockerfile*", "docker-compose*", "requirements*.txt"]
        },
        "testing": {
            "description": "Test Files (Keep)",
            "files": [],
            "patterns": ["test_*.py", "testing/"]
        },
        "archive": {
            "description": "Archive/Backup Files (Consider removing)",
            "files": [],
            "patterns": ["*_backup*", "*_old*", "archive/", "*_new.py"]
        }
    }
    
    # Scan directory
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            file_path = os.path.join(root, file).replace("\\", "/")
            
            # Categorize file
            categorized = False
            for category, info in categories.items():
                for pattern in info["patterns"]:
                    if pattern.endswith("/"):
                        # Directory pattern
                        if pattern.rstrip("/") in file_path:
                            info["files"].append(file_path)
                            categorized = True
                            break
                    else:
                        # File pattern
                        if pattern.startswith("*"):
                            if file.endswith(pattern[1:]):
                                info["files"].append(file_path)
                                categorized = True
                                break
                        elif "*" in pattern:
                            if pattern.replace("*", "") in file:
                                info["files"].append(file_path)
                                categorized = True
                                break
                        else:
                            if file == pattern or file_path.endswith(pattern):
                                info["files"].append(file_path)
                                categorized = True
                                break
                if categorized:
                    break
            
            if not categorized:
                # Uncategorized files
                if "uncategorized" not in categories:
                    categories["uncategorized"] = {"description": "Uncategorized Files", "files": []}
                categories["uncategorized"]["files"].append(file_path)
    
    return categories

def generate_cleanup_report():
    """Generate cleanup recommendations"""
    print("🧹 PROJECT CLEANUP ANALYSIS")
    print("=" * 60)
    
    categories = analyze_project_structure()
    
    # Print analysis
    for category, info in categories.items():
        if info["files"]:
            print(f"\n📁 {info['description'].upper()}")
            print("-" * 40)
            for file in sorted(info["files"])[:10]:  # Show first 10 files
                print(f"   {file}")
            if len(info["files"]) > 10:
                print(f"   ... and {len(info['files']) - 10} more files")
            print(f"   Total: {len(info['files'])} files")
    
    # Cleanup recommendations
    print("\n🎯 CLEANUP RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n✅ KEEP (Essential for Streamlit app):")
    keep_categories = ["streamlit_app", "backend_modules", "data_files", "deployment", "testing"]
    for cat in keep_categories:
        if cat in categories and categories[cat]["files"]:
            print(f"   📁 {categories[cat]['description']}: {len(categories[cat]['files'])} files")
    
    print("\n⚠️  REVIEW (May be legacy):")
    review_categories = ["legacy_flask", "documentation"]
    for cat in review_categories:
        if cat in categories and categories[cat]["files"]:
            print(f"   📁 {categories[cat]['description']}: {len(categories[cat]['files'])} files")
    
    print("\n🗑️  CONSIDER REMOVING:")
    remove_categories = ["archive"]
    for cat in remove_categories:
        if cat in categories and categories[cat]["files"]:
            print(f"   📁 {categories[cat]['description']}: {len(categories[cat]['files'])} files")

if __name__ == "__main__":
    generate_cleanup_report()
