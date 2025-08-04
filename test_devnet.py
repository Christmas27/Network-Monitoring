"""
Test DevNet connectivity - Updated for modules directory
"""

from modules.devnet_integration import DevNetSandboxManager

def test_devnet():
    print("🧪 Testing DevNet Sandbox Connectivity")
    print("=" * 50)
    
    try:
        dm = DevNetSandboxManager()
        print("✅ DevNet manager initialized")
        
        print("\n🔍 Testing all DevNet devices...")
        results = dm.test_all_devices()
        
        print(f"\n📊 Summary: {results['summary']}")
        print(f"✅ Working devices: {len(results['working_devices'])}")
        print(f"❌ Failed devices: {len(results['failed_devices'])}")
        
        if results['working_devices']:
            print("\n🎉 Available devices:")
            for device in results['working_devices']:
                print(f"   - {device}")
        
        if results['failed_devices']:
            print("\n⚠️ Unavailable devices:")
            for device in results['failed_devices']:
                error_msg = results['all_results'][device]['message']
                print(f"   - {device}: {error_msg[:100]}...")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing DevNet: {e}")
        return None

if __name__ == "__main__":
    test_devnet()