import requests
from netmiko import ConnectHandler
from typing import Dict, List
import json
from datetime import datetime
import socket

class DevNetSandboxManager:
    """Integration with Cisco DevNet Always-On Sandbox"""
    
    def __init__(self):
        print("🔧 Initializing DevNet Sandbox Manager...")
        # Multiple DevNet sandbox options with different credentials
        self.sandbox_devices = {
            'ios_xe_latest_v1': {
                'device_type': 'cisco_xe',
                'host': 'sandbox-iosxe-latest-1.cisco.com',
                'username': 'developer',
                'password': 'C1sco12345',
                'port': 22,
                'timeout': 30,
                'conn_timeout': 30
            },
            'ios_xe_latest_v2': {
                'device_type': 'cisco_xe',
                'host': 'sandbox-iosxe-latest-1.cisco.com',
                'username': 'admin',
                'password': 'C1sco12345',
                'port': 22,
                'timeout': 30,
                'conn_timeout': 30
            },
            'ios_xe_latest_v3': {
                'device_type': 'cisco_xe',
                'host': 'sandbox-iosxe-latest-1.cisco.com',
                'username': 'cisco',
                'password': 'cisco',
                'port': 22,
                'timeout': 30,
                'conn_timeout': 30
            },
            'ios_xe_recomm_v1': {
                'device_type': 'cisco_xe',
                'host': 'sandbox-iosxe-recomm-1.cisco.com',
                'username': 'developer',
                'password': 'C1sco12345',
                'port': 22,
                'timeout': 30,
                'conn_timeout': 30
            },
            'ios_xe_recomm_v2': {
                'device_type': 'cisco_xe',
                'host': 'sandbox-iosxe-recomm-1.cisco.com',
                'username': 'admin',
                'password': 'C1sco12345',
                'port': 22,
                'timeout': 30,
                'conn_timeout': 30
            }
        }
        print(f"📱 Configured {len(self.sandbox_devices)} DevNet sandbox variations")
    
    def check_device_reachability(self, device_name: str) -> Dict:
        """Check if device is reachable before attempting SSH"""
        try:
            device = self.sandbox_devices.get(device_name)
            if not device:
                return {'reachable': False, 'error': 'Device not found'}
            
            print(f"🌐 Checking network connectivity to {device['host']}...")
            
            # Test network connectivity first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((device['host'], device['port']))
            sock.close()
            
            if result == 0:
                return {'reachable': True, 'message': f"Port {device['port']} is open on {device['host']}"}
            else:
                return {'reachable': False, 'error': f"Cannot reach {device['host']}:{device['port']}"}
                
        except Exception as e:
            return {'reachable': False, 'error': str(e)}
    
    def test_connectivity(self, device_name: str) -> Dict:
        """Test connection to DevNet sandbox device"""
        print(f"\n🧪 Testing connectivity to {device_name}...")
        
        try:
            device = self.sandbox_devices.get(device_name)
            if not device:
                return {'status': 'error', 'message': 'Device configuration not found'}
            
            # First check if device is reachable
            reachability = self.check_device_reachability(device_name)
            if not reachability['reachable']:
                return {
                    'status': 'error', 
                    'message': f'Device unreachable: {reachability["error"]}',
                    'suggestion': 'The DevNet sandbox might be down or busy'
                }
            
            print(f"✅ Network connectivity OK")
            print(f"🔐 Attempting SSH login with {device['username']}@{device['host']}...")
            
            # Try SSH connection with verbose error handling
            try:
                connection = ConnectHandler(
                    device_type=device['device_type'],
                    host=device['host'],
                    username=device['username'],
                    password=device['password'],
                    port=device['port'],
                    timeout=device.get('timeout', 30),
                    conn_timeout=device.get('conn_timeout', 30),
                    auth_timeout=30,
                    banner_timeout=30,
                    read_timeout_override=30
                )
                
                print(f"✅ SSH connection successful!")
                print(f"📝 Executing test commands...")
                
                # Test basic commands
                version_output = connection.send_command('show version | include Version', delay_factor=3)
                hostname_output = connection.send_command('show running-config | include hostname', delay_factor=3)
                
                connection.disconnect()
                print(f"✅ Commands executed successfully!")
                
                return {
                    'status': 'success',
                    'message': f'Successfully connected to real Cisco device using {device["username"]}!',
                    'device_info': {
                        'version': version_output,
                        'hostname': hostname_output
                    },
                    'host': device['host'],
                    'credentials_used': f"{device['username']}@{device['host']}",
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as ssh_error:
                ssh_error_msg = str(ssh_error)
                print(f"❌ SSH failed with {device['username']}: {ssh_error_msg}")
                
                return {
                    'status': 'error',
                    'message': f'SSH authentication failed with {device["username"]}@{device["host"]}',
                    'error_details': ssh_error_msg,
                    'suggestion': 'Credentials may have changed or sandbox is temporarily unavailable'
                }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Connection failed: {error_msg}")
            
            return {
                'status': 'error', 
                'message': f'Connection failed: {error_msg}',
                'suggestion': 'Check DevNet Sandbox status at https://devnetsandbox.cisco.com',
                'device_attempted': device.get('host', 'Unknown')
            }
    
    def test_all_devices(self) -> Dict:
        """Test connectivity to all configured devices and find working ones"""
        print(f"\n🔍 Testing all {len(self.sandbox_devices)} DevNet sandbox variations...")
        print("=" * 70)
        
        results = {}
        working_devices = []
        failed_devices = []
        
        for device_name in self.sandbox_devices.keys():
            result = self.test_connectivity(device_name)
            results[device_name] = result
            
            if result['status'] == 'success':
                working_devices.append(device_name)
                print(f"✅ {device_name}: SUCCESS")
                # If we find one working device, we can stop testing others for the same host
                device_host = self.sandbox_devices[device_name]['host']
                print(f"🎉 Found working credentials for {device_host}!")
            else:
                failed_devices.append(device_name)
                print(f"❌ {device_name}: FAILED")
        
        summary = f"{len(working_devices)}/{len(self.sandbox_devices)} device configurations working"
        print(f"\n📊 Final Summary: {summary}")
        
        if working_devices:
            print(f"✅ Working configurations:")
            for device in working_devices:
                config = self.sandbox_devices[device]
                print(f"   - {device}: {config['username']}@{config['host']}")
        else:
            print("⚠️  No working DevNet connections found")
            print("💡 Suggestions:")
            print("   1. Check https://devnetsandbox.cisco.com for current status")
            print("   2. Verify internet connectivity")
            print("   3. Try again later (sandboxes are sometimes busy)")
            print("   4. Use simulated mode for demonstration")
        
        return {
            'all_results': results,
            'working_devices': working_devices,
            'failed_devices': failed_devices,
            'summary': summary
        }
    
    def get_working_device(self) -> str:
        """Get the first working device for monitoring"""
        test_results = self.test_all_devices()
        if test_results['working_devices']:
            return test_results['working_devices'][0]
        return None
    
    def get_alternative_test_data(self) -> Dict:
        """Provide simulated data when DevNet is unavailable"""
        return {
            'status': 'simulated',
            'message': '📡 Using simulated Cisco device data (DevNet unavailable)',
            'device_info': {
                'version': 'Cisco IOS XE Software, Version 17.03.04a (simulated)',
                'hostname': 'hostname DEVNET-SANDBOX-SIM',
                'uptime': 'System uptime: 2 days, 14 hours, 30 minutes'
            },
            'interfaces': '''Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       10.10.20.48     YES NVRAM  up                    up      
GigabitEthernet2       unassigned      YES NVRAM  administratively down down    
GigabitEthernet3       unassigned      YES NVRAM  administratively down down    
Loopback0              192.168.1.1     YES manual up                    up''',
            'timestamp': datetime.now().isoformat(),
            'note': 'This is high-quality simulated data for demonstration purposes'
        }
    
    def get_available_devices(self) -> List[Dict]:
        """Get list of available DevNet devices with current status"""
        # Test which devices are currently working
        test_results = self.test_all_devices()
        
        devices = []
        processed_hosts = set()
        
        for name, config in self.sandbox_devices.items():
            host = config['host']
            
            # Only add unique hosts, prefer working configurations
            if host not in processed_hosts:
                is_working = name in test_results['working_devices']
                
                devices.append({
                    'name': name,
                    'host': host,
                    'type': config['device_type'],
                    'status': 'online' if is_working else 'offline',
                    'description': f'Cisco DevNet {host.split(".")[0].replace("-", " ").title()}',
                    'credentials': f"{config['username']}@{host}" if is_working else 'Testing...'
                })
                processed_hosts.add(host)
        
        return devices