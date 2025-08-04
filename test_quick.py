"""
Quick test of dashboard components
"""

def quick_test():
    print("🚀 Quick Dashboard Test")
    print("=" * 30)
    
    # Test 1: Live Monitoring
    try:
        from modules.live_monitoring import LiveNetworkMonitor
        print("✅ LiveNetworkMonitor import: OK")
        
        lm = LiveNetworkMonitor()
        print("✅ LiveNetworkMonitor creation: OK")
        
        data = lm.get_current_data()
        print(f"✅ Current data: {data['mode']} mode, {len(data['devices'])} devices")
        
    except Exception as e:
        print(f"❌ LiveNetworkMonitor error: {e}")
    
    # Test 2: DevNet Integration
    try:
        from modules.devnet_integration import DevNetSandboxManager
        print("✅ DevNetSandboxManager import: OK")
        
        dm = DevNetSandboxManager()
        print("✅ DevNetSandboxManager creation: OK")
        
        devices = dm.get_available_devices()
        print(f"✅ Available devices: {len(devices)} configured")
        
    except Exception as e:
        print(f"❌ DevNetSandboxManager error: {e}")
    
    print("\n🎯 If both tests pass, your dashboard should work!")

if __name__ == "__main__":
    quick_test()