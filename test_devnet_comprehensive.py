"""
Comprehensive DevNet test - tries all configurations
"""

from modules.devnet_integration import DevNetSandboxManager

def comprehensive_test():
    print("🌐 Comprehensive DevNet Sandbox Test")
    print("=" * 50)
    
    try:
        dm = DevNetSandboxManager()
        print("✅ DevNet manager initialized")
        
        # Show all configured devices
        print(f"\n📋 Configured devices ({len(dm.sandbox_devices)}):")
        for name, config in dm.sandbox_devices.items():
            print(f"   - {name}: {config['username']}@{config['host']}")
        
        # Test all devices
        print("\n🧪 Testing all device configurations...")
        results = dm.test_all_devices()
        
        print(f"\n📊 Final Results:")
        print(f"   ✅ Working: {len(results['working_devices'])}")
        print(f"   ❌ Failed: {len(results['failed_devices'])}")
        print(f"   📋 Summary: {results['summary']}")
        
        # If nothing works, show simulation option
        if not results['working_devices']:
            print(f"\n📡 DevNet Unavailable - Testing Simulation Mode:")
            sim_data = dm.get_alternative_test_data()
            print(f"   ✅ Simulation Status: {sim_data['status']}")
            print(f"   📝 Message: {sim_data['message']}")
            print(f"   🔧 Device Info: {sim_data['device_info']['version'][:50]}...")
            
            print(f"\n💡 For Portfolio Purposes:")
            print(f"   ✅ Your dashboard can show professional simulated data")
            print(f"   ✅ Demonstrates your ability to handle real devices")
            print(f"   ✅ Perfect for showcasing network automation skills")
            print(f"   🔄 Will automatically switch to live data when DevNet is available")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during comprehensive test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    comprehensive_test()