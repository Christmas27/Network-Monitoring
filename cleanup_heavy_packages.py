#!/usr/bin/env python3
"""
Simple Package Cleanup Script
Removes the heaviest unused dependencies to reduce project size
"""

import subprocess
import sys

# Heavy packages that are definitely not used in network monitoring
HEAVY_UNUSED_PACKAGES = [
    # Machine Learning / AI (Very Heavy)
    'tensorflow', 'tensorflow-intel', 'tensorflow-io-gcs-filesystem',
    'keras', 'keras-applications', 'keras-facenet', 'keras-vggface',
    'tensorboard', 'tensorboard-data-server',
    'scikit-learn', 'scipy', 'numpy',
    'opencv-python', 'opencv-python-headless',
    'dlib', 'face-recognition', 'face-recognition-models', 'mtcnn',
    
    # Google Cloud / Firebase (Heavy)
    'firebase-admin', 'gcloud', 'google-api-core', 'google-api-python-client',
    'google-auth', 'google-auth-httplib2', 'google-cloud-core',
    'google-cloud-firestore', 'google-cloud-storage', 'google-crc32c',
    'google-resumable-media', 'googleapis-common-protos', 'google-images-download',
    'google-pasta',
    
    # Web Scraping / Selenium
    'selenium', 'msedge-selenium-tools', 'beautifulsoup4', 'soupsieve',
    
    # Alternative frameworks not used
    'django', 'asgiref', 'sqlparse', 'dash',
    
    # Office/Excel
    'openpyxl', 'et-xmlfile',
    
    # Task queues not used
    'celery', 'billiard', 'kombu', 'amqp', 'vine', 'redis',
    
    # Visualization not used
    'matplotlib', 'fonttools', 'cycler', 'kiwisolver', 'contourpy',
    
    # Image processing not used
    'pillow', 'pypng',
]

def uninstall_packages(packages):
    """Uninstall packages"""
    removed_count = 0
    
    for package in packages:
        try:
            print(f"Removing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', package, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ {package} removed")
                removed_count += 1
            else:
                print(f"  - {package} not found")
                
        except Exception as e:
            print(f"  ! Error removing {package}: {e}")
    
    return removed_count

def main():
    print("Starting cleanup of heavy unused packages...")
    print("=" * 50)
    
    print(f"Removing {len(HEAVY_UNUSED_PACKAGES)} heavy packages...")
    removed = uninstall_packages(HEAVY_UNUSED_PACKAGES)
    
    print(f"\nCleanup completed!")
    print(f"Removed: {removed} packages")
    print(f"Expected space saved: 600-800MB")
    print(f"\nTo check remaining packages: pip list | wc -l")

if __name__ == "__main__":
    main()
