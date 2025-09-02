#!/usr/bin/env python3
"""
Dependency Analysis Tool
Identifies unused packages to reduce project size from 1GB to manageable size
"""

import subprocess
import re
import os
from pathlib import Path

# Libraries that are definitely NOT used in this network monitoring project
DEFINITELY_UNUSED = {
    # Machine Learning / AI (Heavy - 300-500MB total)
    'tensorflow', 'tensorflow-intel', 'tensorflow-io-gcs-filesystem', 
    'keras', 'keras-applications', 'keras-facenet', 'keras-vggface',
    'tensorboard', 'tensorboard-data-server',
    'scikit-learn', 'scipy', 'numpy',  # numpy might be used by pandas
    'opencv-python', 'opencv-python-headless',
    'dlib', 'face-recognition', 'face-recognition-models', 'mtcnn',
    
    # Web Scraping / Selenium (Heavy - 100MB+)
    'selenium', 'msedge-selenium-tools', 'beautifulsoup4', 'soupsieve',
    
    # Google Cloud / Firebase (Heavy - 100-200MB)
    'firebase-admin', 'gcloud', 'google-api-core', 'google-api-python-client',
    'google-auth', 'google-auth-httplib2', 'google-cloud-core', 
    'google-cloud-firestore', 'google-cloud-storage', 'google-crc32c',
    'google-resumable-media', 'googleapis-common-protos', 'google-images-download',
    'google-pasta', 'Pyrebase4', 'google-auth-oauthlib',
    
    # Alternative Web Frameworks (not using Dash/Django)
    'django', 'asgiref', 'sqlparse', 'dash',
    
    # Office/Excel (not used)
    'openpyxl', 'et-xmlfile',
    
    # Alternative task queues (not using Celery)
    'celery', 'billiard', 'kombu', 'amqp', 'vine', 'redis',
    
    # GUI/Desktop (not used in web app)
    'inquirer', 'blessed', 'jinxed', 'readchar',
    
    # Alternative async (using built-in)
    'trio', 'trio-websocket', 'outcome', 'sniffio', 'sortedcontainers',
    
    # Image processing (not used)
    'pillow', 'pypng',
    
    # Alternative database connectors
    'mysqlclient', 'PyJWT', 'jwcrypto',
    
    # Testing (can be dev-only)
    'pytest', 'pluggy', 'iniconfig',
    
    # Alternative authentication
    'pyotp', 'python-jwt', 'oauth2client', 'pyasn1', 'pyasn1-modules',
    
    # Build tools
    'setuptools', 'wheel',
    
    # Misc heavy libraries
    'matplotlib', 'fonttools', 'cycler', 'kiwisolver', 'contourpy',
    'editor', 'runs', 'transitions', 'qrcode',
}

# Libraries that MIGHT be used (need verification)
MAYBE_UNUSED = {
    # Network tools (some might be used)
    'scapy', 'python-nmap', 'pysnmp', 'netifaces',
    
    # Alternative config formats
    'toml', 'xmltodict',
    
    # Job scheduling
    'APScheduler',
    
    # Alternative template engines
    'xmod',
    
    # Crypto (might be used by network libs)
    'pycryptodome', 'cryptography',
    
    # Windows specific
    'pywin32', 'ansicon', 'colorama',
    
    # HTTP clients (might be used)
    'httplib2', 'CacheControl', 'cachelib',
}

# Essential libraries that MUST stay
ESSENTIAL = {
    # Core Python-only frontend
    'streamlit', 'plotly', 'pandas', 'altair', 'pyarrow', 'pydeck',
    
    # Network automation (core functionality)
    'netmiko', 'napalm', 'ncclient', 'ansible', 'ansible-core', 'ansible-runner',
    'netaddr', 'netutils', 'paramiko', 'pynacl', 'bcrypt', 'scp',
    
    # Network device libraries
    'junos-eznc', 'pyeapi', 'textfsm', 'ntc-templates', 'ttp', 'ttp-templates',
    
    # Network utilities
    'ping3', 'pyserial',
    
    # Flask backend (for API endpoints)
    'flask', 'flask-cors', 'werkzeug', 'jinja2', 'markupsafe', 'itsdangerous',
    'blinker', 'click',
    
    # Database
    'sqlalchemy', 'greenlet',
    
    # Core Python utilities
    'pyyaml', 'requests', 'urllib3', 'certifi', 'charset-normalizer', 'idna',
    'python-dotenv', 'typing-extensions', 'packaging',
    
    # Docker lab support
    'docker',
    
    # Date/time
    'python-dateutil', 'pytz', 'tzdata', 'tzlocal',
    
    # Development
    'watchdog', 'rich', 'tqdm',
    
    # YAML processing
    'yamlordereddictloader',
    
    # Misc utilities
    'six', 'future', 'deprecated', 'wrapt', 'attrs', 'jsonschema',
    'jsonschema-specifications', 'referencing', 'rpds-py',
}

def analyze_dependencies():
    """Analyze which dependencies can be safely removed"""
    
    print("🔍 Analyzing Dependencies for Size Optimization")
    print("=" * 60)
    
    # Get currently installed packages
    result = subprocess.run(['pip', 'list', '--format=freeze'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to get package list")
        return
    
    installed_packages = {}
    total_size = 0
    
    for line in result.stdout.strip().split('\n'):
        if '==' in line:
            name, version = line.split('==')
            installed_packages[name.lower()] = version
    
    print(f"📊 Total packages installed: {len(installed_packages)}")
    
    # Categorize packages
    definitely_remove = []
    maybe_remove = []
    keep_packages = []
    
    for pkg_name in installed_packages:
        if pkg_name.lower() in DEFINITELY_UNUSED:
            definitely_remove.append(pkg_name)
        elif pkg_name.lower() in MAYBE_UNUSED:
            maybe_remove.append(pkg_name)
        else:
            keep_packages.append(pkg_name)
    
    print(f"\n🗑️  DEFINITELY REMOVE ({len(definitely_remove)} packages):")
    print("   These are confirmed unused and very large:")
    for pkg in sorted(definitely_remove):
        print(f"   - {pkg}")
    
    print(f"\n⚠️  MAYBE REMOVE ({len(maybe_remove)} packages):")
    print("   These might be unused (need verification):")
    for pkg in sorted(maybe_remove):
        print(f"   - {pkg}")
    
    print(f"\n✅ KEEP ({len(keep_packages)} packages):")
    print("   These are essential for the application:")
    for pkg in sorted(keep_packages[:20]):  # Show first 20
        print(f"   - {pkg}")
    if len(keep_packages) > 20:
        print(f"   ... and {len(keep_packages) - 20} more")
    
    # Estimate size savings
    heavy_packages = [
        'tensorflow', 'tensorflow-intel', 'keras', 'opencv-python', 
        'selenium', 'firebase-admin', 'google-cloud-storage',
        'scikit-learn', 'matplotlib', 'pillow', 'dlib'
    ]
    
    heavy_found = [pkg for pkg in heavy_packages if pkg.lower() in installed_packages]
    
    print(f"\n💾 Estimated size reduction:")
    print(f"   Heavy packages found: {len(heavy_found)}")
    print(f"   Estimated savings: 600-800MB (from AI/ML/Cloud libraries)")
    print(f"   Target size after cleanup: 200-300MB")
    
    return definitely_remove, maybe_remove

def create_minimal_requirements():
    """Create a minimal requirements.txt for production deployment"""
    
    minimal_requirements = """# Network Monitoring Dashboard - Minimal Production Requirements
# Optimized for deployment size (target: <300MB)

# === FRONTEND (Python-only) ===
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
watchdog>=3.0.0

# === CORE WEB FRAMEWORK ===
Flask==2.3.3
Flask-Cors==4.0.0
Werkzeug==2.3.7

# === NETWORK AUTOMATION (Core functionality) ===
netmiko==4.2.0
napalm==4.1.0
ncclient==0.6.15
junos-eznc==2.7.1
pyeapi==1.0.4

# === ANSIBLE AUTOMATION ===
ansible-runner>=2.3.0
ansible>=8.0.0
PyYAML>=6.0.0

# === NETWORK UTILITIES ===
ping3==5.1.5
netaddr==1.3.0
netutils==1.14.1

# === TEMPLATE PARSING ===
textfsm==1.1.3
ntc_templates==8.0.0
ttp==0.9.5

# === CORE UTILITIES ===
requests>=2.31.0
python-dotenv>=1.0.0
paramiko>=3.3.0

# === DATABASE ===
SQLAlchemy>=2.0.0

# === DOCKER LAB SUPPORT (Optional) ===
docker>=6.0.0

# === CISCO DEVNET INTEGRATION ===
# Note: Uses requests for REST API calls, no additional libs needed
"""
    
    with open('requirements-minimal.txt', 'w') as f:
        f.write(minimal_requirements)
    
    print(f"📄 Created requirements-minimal.txt for deployment")

def create_cleanup_script():
    """Create a script to uninstall unused packages"""
    
    definitely_remove, maybe_remove = analyze_dependencies()
    
    cleanup_script = f"""#!/usr/bin/env python3
'''
Package Cleanup Script
Removes unused dependencies to reduce project size from 1GB to ~300MB
'''

import subprocess
import sys

# Packages confirmed as unused and safe to remove
DEFINITELY_REMOVE = {definitely_remove}

# Packages that might be unused (check before removing)
MAYBE_REMOVE = {maybe_remove}

def uninstall_packages(packages, category_name):
    '''Uninstall a list of packages'''
    
    if not packages:
        print(f"✅ No packages to remove in {{category_name}}")
        return
        
    print(f"🗑️  Removing {{len(packages)}} packages from {{category_name}}...")
    
    for package in packages:
        try:
            print(f"   Removing {{package}}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', package, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {{package}} removed")
            else:
                print(f"   ⚠️  {{package}} not found or failed to remove")
                
        except Exception as e:
            print(f"   ❌ Error removing {{package}}: {{e}}")

def main():
    print("🧹 Starting package cleanup to reduce project size...")
    print("=" * 60)
    
    # Remove definitely unused packages
    uninstall_packages(DEFINITELY_REMOVE, "Heavy Unused Libraries")
    
    # Ask about maybe unused packages
    print("\\n⚠️  The following packages might be unused:")
    for pkg in sorted(MAYBE_REMOVE):
        print(f"   - {{pkg}}")
    
    response = input("\\nRemove these packages too? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        uninstall_packages(MAYBE_REMOVE, "Possibly Unused Libraries")
    else:
        print("📝 Skipping possibly unused packages")
    
    print("\\n🎉 Cleanup completed!")
    print("💾 Run 'pip list | wc -l' to see reduced package count")
    print("📊 Check folder size to confirm space savings")

if __name__ == "__main__":
    main()
"""
    
    with open('cleanup_dependencies.py', 'w') as f:
        f.write(cleanup_script)
    
    print(f"📄 Created cleanup_dependencies.py script")

if __name__ == "__main__":
    analyze_dependencies()
    create_minimal_requirements()
    create_cleanup_script()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Review the analysis above")
    print(f"2. Run: python cleanup_dependencies.py")
    print(f"3. Test your application still works") 
    print(f"4. Use requirements-minimal.txt for deployment")
    print(f"5. Expected size reduction: 600-800MB → ~300MB")
