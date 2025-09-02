#!/usr/bin/env python3
"""
Safe Cleanup Script - Remove Legacy Files Before GitHub Push
"""

import os
import shutil
from pathlib import Path

def safe_cleanup():
    """Remove legacy Flask files and archives safely"""
    
    print("🧹 STARTING SAFE CLEANUP")
    print("=" * 40)
    
    # Files/folders to remove
    cleanup_targets = [
        # Legacy Flask files
        "main.py",
        "templates/",
        "static/",
        
        # Archive/backup files  
        "streamlit_app_backup.py",
        "streamlit_app_new.py",
        "archive/",
        
        # Test files (optional)
        "test_*.py",
        "analyze_structure.py",
        "quick_analysis.py",
        "DOUBLE_SIDEBAR_SOLVED.py",
        "ISSUE_RESOLUTION_COMPLETE.py",
        "SIDEBAR_FIX_EXPLANATION.py",
        
        # Other legacy files
        "automation_section_fixed.py"
    ]
    
    # Create backup directory first
    backup_dir = Path("cleanup_backup")
    backup_dir.mkdir(exist_ok=True)
    
    removed_count = 0
    
    for target in cleanup_targets:
        if os.path.exists(target):
            try:
                # Backup before removing
                backup_path = backup_dir / target.replace("/", "_")
                
                if os.path.isdir(target):
                    shutil.copytree(target, backup_path, dirs_exist_ok=True)
                    shutil.rmtree(target)
                    print(f"🗑️  Removed directory: {target}")
                else:
                    shutil.copy2(target, backup_path)
                    os.remove(target)
                    print(f"🗑️  Removed file: {target}")
                
                removed_count += 1
                
            except Exception as e:
                print(f"❌ Error removing {target}: {e}")
        else:
            print(f"⚪ Not found: {target}")
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} items")
    print(f"📁 Backups saved in: cleanup_backup/")
    
    # Show final structure
    print(f"\n📂 CLEAN PROJECT STRUCTURE:")
    essential_items = [
        "streamlit_app.py", "app_pages/", "components/", "utils/",
        "modules/", "config/", "data/", "ansible_playbooks/",
        "requirements.txt", "README.md"
    ]
    
    for item in essential_items:
        if os.path.exists(item):
            print(f"   ✅ {item}")
        else:
            print(f"   ❓ {item} (missing)")

if __name__ == "__main__":
    # Ask for confirmation
    print("⚠️  This will remove legacy Flask files and create backups.")
    print("📁 Backups will be saved in 'cleanup_backup/' folder.")
    
    choice = input("\\nProceed with cleanup? (y/N): ").lower().strip()
    
    if choice == 'y':
        safe_cleanup()
        print("\\n🎉 Ready for GitHub push!")
    else:
        print("\\n⏸️  Cleanup cancelled.")
