# Create: test_catalyst_only.py
"""
Test Catalyst Center integration only (no DevNet)
"""

def test_catalyst_center_only():
    print("🚀 Testing Catalyst Center Integration Only")
    print("=" * 50)
    
    try:
        from modules.catalyst_center_integration import CatalystCenterManager
        print("✅ Catalyst Center import: OK")
        
        cc = CatalystCenterManager()
        print("✅ Catalyst Center manager created")
        
        # Test connection
        result = cc.test_connection()
        print(f"🧪 Connection test: {result['status']}")
        print(f"📄 Message: {result['message']}")
        
        if result['status'] == 'success':
            print(f"🎉 SUCCESS!")
            print(f"   📱 Devices found: {result['device_count']}")
            print(f"   🌐 Lab URL: {result['lab_info']['url']}")
            print(f"   👤 Username: {result['lab_info']['username']}")
        else:
            print(f"⚠️ Catalyst Center not available")
            print(f"   📄 Suggestion: {result.get('suggestion', 'Check lab status')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test live monitoring without DevNet
    try:
        print(f"\n🔍 Testing Live Monitoring (without DevNet)...")
        from modules.live_monitoring import LiveNetworkMonitor
        
        lm = LiveNetworkMonitor()
        print("✅ Live monitoring created successfully")
        
        data = lm.get_current_data()
        print(f"✅ Current mode: {data['mode']}")
        print(f"✅ Devices available: {len(data['devices'])}")
        
    except Exception as e:
        print(f"❌ Live monitoring error: {e}")

if __name__ == "__main__":
    test_catalyst_center_only()