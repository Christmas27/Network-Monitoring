"""
Simple DevNet test - Fixed device names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.devnet_integration import DevNetSandboxManager
    print("✅ Import successful")
    
    dm = DevNetSandboxManager()
    print("✅ DevNet manager created")
    
    # Show available device names
    print("\n📋 Available device configurations:")
    for name in dm.sandbox_devices.keys():
        config = dm.sandbox_devices[name]
        print(f"   - {name}: {config['username']}@{config['host']}")
    
    # Test the first available device
    first_device = list(dm.sandbox_devices.keys())[0]
    print(f"\n🔍 Testing device: {first_device}")
    result = dm.test_connectivity(first_device)
    print(f"📊 Result: {result['status']}")
    print(f"📝 Message: {result['message']}")
    
    if result['status'] == 'error':
        print(f"💡 Suggestion: {result.get('suggestion', 'Try another device')}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Current directory:", os.getcwd())
    print("📂 Available directories:", [d for d in os.listdir('.') if os.path.isdir(d)])
    
except Exception as e:
    print(f"❌ Other error: {e}")