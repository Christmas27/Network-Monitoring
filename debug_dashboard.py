"""
Debug script to test dashboard components
"""

def test_dashboard_components():
    print("🔍 Testing dashboard components...")
    
    try:
        from modules.devnet_integration import DevNetSandboxManager
        print("✅ DevNet integration import: OK")
        
        dm = DevNetSandboxManager()
        print("✅ DevNet manager creation: OK")
        
    except Exception as e:
        print(f"❌ DevNet integration error: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        from modules.live_monitoring import LiveNetworkMonitor
        print("✅ Live monitoring import: OK")
        
        lm = LiveNetworkMonitor()
        print("✅ Live monitor creation: OK")
        
        # Test getting data without starting monitoring
        data = lm.get_current_data()
        print(f"✅ Live monitor data: {len(data)} keys")
        
    except Exception as e:
        print(f"❌ Live monitoring error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test other existing modules
    try:
        from modules.device_manager import DeviceManager
        dm = DeviceManager()
        devices = dm.get_all_devices()
        print(f"✅ Device manager: {len(devices)} devices")
    except Exception as e:
        print(f"❌ Device manager error: {e}")
    
    try:
        from modules.network_monitor import NetworkMonitor
        nm = NetworkMonitor()
        print("✅ Network monitor: OK")
    except Exception as e:
        print(f"❌ Network monitor error: {e}")

if __name__ == "__main__":
    test_dashboard_components()