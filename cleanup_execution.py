#!/usr/bin/env python3
"""
Cleanup Execution Script
Organizes and removes legacy files after Streamlit migration
"""
import os
import shutil
import sys
from pathlib import Path

def cleanup_legacy_files():
    """Remove legacy Flask files"""
    legacy_files = [
        'main.py',
        'templates',
        'static',
        'docker guide.txt',  # Duplicate of Dockerfile info
    ]
    
    print("🧹 Cleaning up legacy files...")
    for item in legacy_files:
        if os.path.exists(item):
            if os.path.isfile(item):
                os.remove(item)
                print(f"  ✅ Removed file: {item}")
            elif os.path.isdir(item):
                shutil.rmtree(item)
                print(f"  ✅ Removed directory: {item}")
        else:
            print(f"  ℹ️  Not found: {item}")

def organize_directories():
    """Create organized directory structure"""
    
    # Create docs directory
    if not os.path.exists('docs'):
        os.makedirs('docs')
        print("📁 Created docs/ directory")
    
    # Move documentation files
    doc_files = [
        'API_DOCUMENTATION.md',
        'ARCHITECTURE.md', 
        'DEPLOYMENT.md',
        'README.md'
    ]
    
    for doc in doc_files:
        if os.path.exists(doc) and doc != 'README.md':  # Keep README.md in root
            shutil.move(doc, f'docs/{doc}')
            print(f"  📄 Moved {doc} to docs/")
    
    # Create database directory structure
    if not os.path.exists('database'):
        os.makedirs('database')
        print("📁 Created database/ directory")
    
    # Move database files
    db_files = ['data/configurations.db', 'data/devices.db', 'data/monitoring.db', 'data/security.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            filename = os.path.basename(db_file)
            shutil.move(db_file, f'database/{filename}')
            print(f"  🗄️  Moved {filename} to database/")
    
    # Remove empty data directory if it exists
    if os.path.exists('data') and not os.listdir('data'):
        os.rmdir('data')
        print("  ✅ Removed empty data/ directory")

def update_streamlit_config():
    """Update streamlit app to use new database paths"""
    print("🔧 Updating database paths in config...")
    
    # Update config.py to use new database paths
    config_file = 'config/config.py'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update database paths
        content = content.replace('data/configurations.db', 'database/configurations.db')
        content = content.replace('data/devices.db', 'database/devices.db')
        content = content.replace('data/monitoring.db', 'database/monitoring.db')
        content = content.replace('data/security.db', 'database/security.db')
        
        with open(config_file, 'w') as f:
            f.write(content)
        print("  ✅ Updated config/config.py with new database paths")

def create_project_structure():
    """Show final project structure"""
    print("\n📋 Final Project Structure:")
    print("""
DevOps Project - Local/
├── 📱 streamlit_app.py          # Main application
├── 📋 README.md                 # Project overview
├── 🐳 Dockerfile                # Container setup
├── 🐳 docker-compose.yml        # Multi-container orchestration
├── ⚙️  config.json              # Application configuration
├── 📦 requirements.txt          # Python dependencies
├── 
├── 📁 app_pages/                # Streamlit pages
│   ├── automation.py
│   ├── configuration.py
│   ├── dashboard.py
│   ├── devices.py
│   ├── monitoring.py
│   ├── security.py
│   └── topology.py
├── 
├── 📁 components/               # Reusable UI components
├── 📁 utils/                    # Utility functions
├── 📁 modules/                  # Core business logic
├── 📁 config/                   # Configuration files
├── 
├── 📁 database/                 # Database files
│   ├── configurations.db
│   ├── devices.db
│   ├── monitoring.db
│   └── security.db
├── 
├── 📁 docs/                     # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── 
├── 📁 logs/                     # Application logs
├── 📁 backups/                  # Backup files
└── 📁 testing/                  # Test files
    """)

if __name__ == "__main__":
    print("🚀 Starting cleanup process...\n")
    
    # Ask for confirmation
    response = input("Continue with cleanup? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Cleanup cancelled")
        sys.exit(0)
    
    try:
        cleanup_legacy_files()
        organize_directories()
        update_streamlit_config()
        create_project_structure()
        
        print("\n✅ Cleanup completed successfully!")
        print("🔄 Run 'git status' to see changes")
        print("📝 Review changes and commit when ready")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)
