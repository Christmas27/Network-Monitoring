# Create: test_catalyst_simple.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.catalyst_center_integration import CatalystCenterManager

def test_catalyst_step_by_step():
    print("🧪 Step-by-Step Catalyst Center Test")
    print("=" * 50)
    
    try:
        # Step 1: Create manager
        print("🔧 Step 1: Creating Catalyst Center Manager...")
        cc = CatalystCenterManager()
        print(f"✅ Manager created")
        print(f"   URL: {cc.base_url}")
        print(f"   Username: {cc.username}")
        print(f"   Password: {'*' * len(cc.password)}")
        
        # Step 2: Test authentication
        print("\n🔐 Step 2: Testing Authentication...")
        auth_result = cc.authenticate()
        print(f"   Auth result: {auth_result}")
        
        if auth_result:
            print(f"   ✅ Authentication successful!")
            print(f"   🔑 Token received: {cc.auth_token[:50]}..." if cc.auth_token else "No token")
            
            # Step 3: Test device inventory
            print("\n📱 Step 3: Testing Device Inventory...")
            devices = cc.get_device_inventory()
            print(f"   📊 Devices returned: {len(devices)}")
            
            if devices:
                print(f"   📋 First device structure:")
                first_device = devices[0]
                for key, value in first_device.items():
                    print(f"      {key}: {value}")
            else:
                print("   ⚠️ No devices returned")
                
        else:
            print("   ❌ Authentication failed!")
            print("   💡 Check your Catalyst Center credentials")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_catalyst_step_by_step()