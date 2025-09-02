#!/usr/bin/env python3
"""
Quick File Structure Analysis
"""

import os

def analyze_structure():
    print("🧹 PROJECT STRUCTURE ANALYSIS")
    print("=" * 50)
    
    # Legacy Flask files
    legacy_files = []
    if os.path.exists("templates"):
        legacy_files.extend([f"templates/{f}" for f in os.listdir("templates")])
    if os.path.exists("static"):
        for root, dirs, files in os.walk("static"):
            for file in files:
                legacy_files.append(os.path.join(root, file).replace("\\", "/"))
    
    # Check for main.py (Flask)
    if os.path.exists("main.py"):
        legacy_files.append("main.py")
    
    # Streamlit files
    streamlit_files = ["streamlit_app.py", "app_pages/", "components/", "utils/"]
    
    # Backend files (keep)
    backend_files = ["modules/", "config/", "data/"]
    
    # Archive/backup files
    archive_files = []
    for file in os.listdir("."):
        if "backup" in file or "old" in file or "_new" in file:
            archive_files.append(file)
    if os.path.exists("archive"):
        archive_files.append("archive/")
    
    print("\n🔴 LEGACY FLASK FILES (Consider removing):")
    for file in legacy_files:
        print(f"   {file}")
    
    print(f"\n🟢 CURRENT STREAMLIT FILES (Keep):")
    for item in streamlit_files:
        if os.path.exists(item):
            print(f"   ✅ {item}")
        else:
            print(f"   ❓ {item} (not found)")
    
    print(f"\n🔵 BACKEND FILES (Keep):")
    for item in backend_files:
        if os.path.exists(item):
            print(f"   ✅ {item}")
    
    print(f"\n🟡 ARCHIVE/BACKUP FILES (Review):")
    for file in archive_files:
        print(f"   {file}")
    
    print("\n📋 CLEANUP SUMMARY:")
    print("=" * 50)
    print(f"Legacy Flask files: {len(legacy_files)}")
    print(f"Archive/backup files: {len(archive_files)}")
    print(f"Total files to review: {len(legacy_files) + len(archive_files)}")

if __name__ == "__main__":
    analyze_structure()
