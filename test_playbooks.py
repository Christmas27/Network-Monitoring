#!/usr/bin/env python3
"""
Test Playbook Detection - Verify Ansible Playbooks are Found
"""

import os
import glob
import sys

def test_playbook_detection():
    """Test if playbooks can be detected in the project"""
    print("🔍 Testing Playbook Detection")
    print("=" * 50)
    
    # Check directories
    playbook_dirs = ['ansible_playbooks', 'ansible_projects/playbooks']
    
    total_playbooks = 0
    
    for directory in playbook_dirs:
        print(f"\n📁 Checking directory: {directory}")
        
        if os.path.exists(directory):
            print(f"✅ Directory exists")
            
            # Find YAML files
            yml_files = glob.glob(f"{directory}/*.yml") + glob.glob(f"{directory}/*.yaml")
            
            if yml_files:
                print(f"📚 Found {len(yml_files)} playbook(s):")
                for file in yml_files:
                    filename = os.path.basename(file)
                    name = filename.replace('.yml', '').replace('.yaml', '')
                    print(f"   • {name} ({filename})")
                    total_playbooks += 1
            else:
                print("⚠️ No YAML files found")
        else:
            print(f"❌ Directory does not exist")
    
    print(f"\n🎯 Total playbooks found: {total_playbooks}")
    
    if total_playbooks > 0:
        print("✅ Playbook detection working correctly!")
        return True
    else:
        print("❌ No playbooks detected - check directories and files")
        return False

def test_ansible_manager():
    """Test if ansible manager can get playbooks"""
    print("\n🤖 Testing Ansible Manager Playbook Detection")
    print("=" * 50)
    
    try:
        # Add current directory to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from modules.ansible_manager_simple import AnsibleManager
        
        ansible_mgr = AnsibleManager()
        print("✅ Ansible Manager initialized")
        
        if hasattr(ansible_mgr, 'get_available_playbooks'):
            playbooks = ansible_mgr.get_available_playbooks()
            print(f"📚 Manager found {len(playbooks)} playbooks:")
            
            for pb in playbooks:
                if isinstance(pb, dict):
                    name = pb.get('name', 'Unknown')
                    desc = pb.get('description', 'No description')
                    print(f"   • {name}: {desc}")
                else:
                    print(f"   • {pb}")
            
            return len(playbooks)
        else:
            print("❌ Manager doesn't have get_available_playbooks method")
            return 0
            
    except Exception as e:
        print(f"❌ Error testing ansible manager: {e}")
        return 0

if __name__ == "__main__":
    test1 = test_playbook_detection()
    count = test_ansible_manager()
    
    print("\n" + "=" * 50)
    if test1 and count > 0:
        print("✅ All playbook tests passed!")
    else:
        print("❌ Some playbook tests failed - check above for details")
