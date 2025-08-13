import requests
import json
from datetime import datetime
from typing import Dict, List
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CatalystCenterManager:
    """Integration with Cisco Catalyst Center Always-On Lab"""
    
    def __init__(self):
        """Initialize with Catalyst Center Always-On credentials"""
        print("🚀 Initializing Catalyst Center Integration...")
        
        # Catalyst Center Always-On Lab credentials
        self.base_url = "https://sandboxdnac2.cisco.com"  # Update with your lab URL
        self.username = "devnetuser"  # Update with your username
        self.password = "Cisco123!"   # Update with your password
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        self.auth_token = None
        self.session = requests.Session()
        self.session.verify = False  # For sandbox environments
        
        print(f"🌐 Catalyst Center URL: {self.base_url}")
        print(f"👤 Username: {self.username}")
    
    def authenticate(self) -> bool:
        """Authenticate with Catalyst Center and get token"""
        try:
            auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
            
            print(f"🔐 Authenticating with Catalyst Center...")
            
            response = self.session.post(
                auth_url,
                auth=(self.username, self.password),
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.auth_token = response.json().get('Token')
                self.headers['X-Auth-Token'] = self.auth_token
                print(f"✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_device_inventory(self) -> List[Dict]:
        """Get all devices from Catalyst Center"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return []
            
            devices_url = f"{self.base_url}/dna/intent/api/v1/network-device"
            
            print(f"📱 Fetching device inventory...")
            
            response = self.session.get(
                devices_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                devices_data = response.json()
                devices = devices_data.get('response', [])
                
                print(f"✅ Found {len(devices)} devices in Catalyst Center")
                
                # Format devices for your dashboard
                formatted_devices = []
                for device in devices:
                    formatted_devices.append({
                        'id': device.get('id'),
                        'name': device.get('hostname', 'Unknown'),
                        'host': device.get('managementIpAddress', 'Unknown'),
                        'type': device.get('family', 'Unknown'),
                        'status': 'online' if device.get('reachabilityStatus') == 'Reachable' else 'offline',
                        'description': f"{device.get('platformId', 'Cisco')} - {device.get('softwareVersion', 'Unknown')}",
                        'series': device.get('series', 'Unknown'),
                        'location': device.get('location', 'Unknown'),
                        'role': device.get('role', 'Unknown'),
                        'response_time': 'Live',
                        'last_check': datetime.now().isoformat()
                    })
                
                return formatted_devices
            else:
                print(f"❌ Failed to get devices: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting device inventory: {e}")
            return []
    
    def get_network_health(self) -> Dict:
        """Get overall network health from Catalyst Center"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {}
            
            health_url = f"{self.base_url}/dna/intent/api/v1/network-health"
            
            response = self.session.get(
                health_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get('response', [])
            else:
                print(f"❌ Failed to get network health: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting network health: {e}")
            return {}
    
    def get_client_health(self) -> Dict:
        """Get client health information"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {}
            
            clients_url = f"{self.base_url}/dna/intent/api/v1/client-health"
            
            response = self.session.get(
                clients_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get client health: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting client health: {e}")
            return {}
    
    def test_connection(self) -> Dict:
        """Test connection to Catalyst Center"""
        try:
            print(f"🧪 Testing Catalyst Center connection...")
            
            # Test authentication
            if self.authenticate():
                # Get basic info
                devices = self.get_device_inventory()
                health = self.get_network_health()
                
                return {
                    'status': 'success',
                    'message': f'Successfully connected to Catalyst Center!',
                    'device_count': len(devices),
                    'lab_info': {
                        'url': self.base_url,
                        'username': self.username,
                        'devices_found': len(devices),
                        'features': ['Device Inventory', 'Network Health', 'Client Monitoring', 'Policy Management']
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to authenticate with Catalyst Center',
                    'suggestion': 'Check credentials and lab availability'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {str(e)}',
                'suggestion': 'Verify lab URL and network connectivity'
            }
    
    def get_device_details(self, device_id: str) -> Dict:
        """Get detailed information for a specific device"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {}
            
            device_url = f"{self.base_url}/dna/intent/api/v1/network-device/{device_id}"
            
            response = self.session.get(
                device_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get device details: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting device details: {e}")
            return {}
    
    def get_device_interfaces(self, device_id: str) -> List[Dict]:
        """Get interface information for a device"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return []
            
            interfaces_url = f"{self.base_url}/dna/intent/api/v1/interface/network-device/{device_id}"
            
            response = self.session.get(
                interfaces_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', [])
            else:
                print(f"❌ Failed to get interfaces: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting interfaces: {e}")
            return []
    
    def get_network_topology(self) -> Dict:
        """Get network topology information"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {}
            
            topology_url = f"{self.base_url}/dna/intent/api/v1/topology/physical-topology"
            
            response = self.session.get(
                topology_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get topology: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting topology: {e}")
            return {}
    
    def create_network_profile(self, profile_data: Dict) -> Dict:
        """Create a new network profile (example POST operation)"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {}
            
            profile_url = f"{self.base_url}/dna/intent/api/v1/network-profile"
            
            response = self.session.post(
                profile_url,
                headers=self.headers,
                json=profile_data,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                return response.json()
            else:
                print(f"❌ Failed to create profile: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error creating profile: {e}")
            return {}
    
    def get_network_topology_for_visualization(self) -> Dict:
        """Get network topology specifically formatted for visualization"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return {'error': 'Authentication failed'}
            
            print("🌐 Fetching network topology for visualization...")
            
            # Get devices first
            devices = self.get_device_inventory()
            
            # Try to get physical topology
            topology_url = f"{self.base_url}/dna/intent/api/v1/topology/physical-topology"
            
            response = self.session.get(
                topology_url,
                headers=self.headers,
                timeout=30
            )
            
            topology_data = {}
            if response.status_code == 200:
                topology_data = response.json()
                print(f"✅ Got topology data from Catalyst Center")
            else:
                print(f"⚠️ Could not get topology links (status: {response.status_code})")
            
            # Format for visualization
            return {
                'status': 'success',
                'devices': devices,
                'topology': topology_data,
                'device_count': len(devices),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting topology for visualization: {e}")
            return {'error': str(e)}
    
    def get_device_neighbors(self, device_id: str) -> List[Dict]:
        """Get neighboring devices for topology mapping"""
        try:
            if not self.auth_token:
                if not self.authenticate():
                    return []
            
            neighbors_url = f"{self.base_url}/dna/intent/api/v1/topology/l2/{device_id}"
            
            response = self.session.get(
                neighbors_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', [])
            else:
                print(f"❌ Failed to get neighbors for {device_id}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting device neighbors: {e}")
            return []

def test_catalyst_center():
    """Quick test function"""
    print("🚀 Testing Catalyst Center Always-On Lab")
    print("=" * 50)
    
    cc = CatalystCenterManager()
    result = cc.test_connection()
    
    print(f"\n📊 Test Results:")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'success':
        print(f"🎉 SUCCESS! Your dashboard can now use:")
        print(f"   📱 {result['device_count']} real network devices")
        print(f"   🌐 Live Catalyst Center APIs")
        print(f"   📊 Real network health data")
        print(f"   👥 Client monitoring")
        print(f"   🔧 Policy management")

if __name__ == "__main__":
    test_catalyst_center()