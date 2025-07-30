#!/usr/bin/env python3
"""
Quick test script to validate the network automation dashboard setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"   ❌ Flask import failed: {e}")
        return False
    
    try:
        import netmiko
        print(f"   ✅ Netmiko {netmiko.__version__}")
    except ImportError as e:
        print(f"   ❌ Netmiko import failed: {e}")
        return False
    
    try:
        import yaml
        print(f"   ✅ PyYAML available")
    except ImportError as e:
        print(f"   ❌ PyYAML import failed: {e}")
        return False
    
    try:
        import requests
        print(f"   ✅ Requests {requests.__version__}")
    except ImportError as e:
        print(f"   ❌ Requests import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'modules',
        'templates', 
        'static',
        'static/css',
        'static/js',
        'config'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory} (missing)")
            all_exist = False
    
    return all_exist

def test_files():
    """Test if required files exist"""
    print("\n📄 Testing core files...")
    
    required_files = [
        'main.py',
        'config.json',
        'requirements.txt',
        'modules/__init__.py',
        'modules/device_manager.py',
        'modules/network_monitor.py',
        'modules/config_manager.py',
        'modules/security_scanner.py',
        'templates/base.html',
        'templates/dashboard.html',
        'static/css/dashboard.css',
        'static/js/dashboard.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🔍 Network Automation Dashboard - Setup Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test directories
    if test_directories():
        tests_passed += 1
    
    # Test files
    if test_files():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Open: http://localhost:5000")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
