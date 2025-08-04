import threading
import time
from datetime import datetime
import json

class LiveNetworkMonitor:
    """Real-time network monitoring with DevNet fallback"""
    
    def __init__(self):
        try:
            from .devnet_integration import DevNetSandboxManager
            self.devnet = DevNetSandboxManager()
        except ImportError:
            print("⚠️ DevNet integration not available - using simulation only")
            self.devnet = None
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.use_simulation = True  # Default to simulation
        self.network_data = {
            'devices': {},
            'alerts': [],
            'performance': {},
            'last_update': None,
            'mode': 'simulated'  # Default to simulated
        }
        
        # Initialize with simulated data immediately
        self._setup_simulated_devices()
    
    def start_monitoring(self):
        """Start monitoring with automatic fallback to simulation"""
        if not self.monitoring_active:
            # Test DevNet availability only if devnet manager exists
            if self.devnet:
                try:
                    print("🧪 Testing DevNet availability...")
                    test_results = self.devnet.test_all_devices()
                    
                    if len(test_results['working_devices']) > 0:
                        print(f"🌐 DevNet available: {len(test_results['working_devices'])} devices")
                        self.use_simulation = False
                        self.network_data['mode'] = 'live'
                    else:
                        print("📡 DevNet unavailable - Using simulation mode")
                        self.use_simulation = True
                        self.network_data['mode'] = 'simulated'
                except Exception as e:
                    print(f"⚠️ DevNet test failed: {e} - Using simulation")
                    self.use_simulation = True
                    self.network_data['mode'] = 'simulated'
            else:
                print("📡 DevNet not configured - Using simulation mode")
                self.use_simulation = True
                self.network_data['mode'] = 'simulated'
            
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print(f"🔄 Started monitoring in {self.network_data['mode'].upper()} mode")
    
    def _setup_simulated_devices(self):
        """Setup simulated device data"""
        simulated_devices = {
            'sim_router_1': {
                'status': 'online',
                'last_check': datetime.now().isoformat(),
                'response_time': '25ms',
                'interface_count': 5,
                'device_info': 'Cisco IOS XE (Simulated)',
                'hostname': 'SIM-ROUTER-1'
            },
            'sim_switch_1': {
                'status': 'online',
                'last_check': datetime.now().isoformat(),
                'response_time': '15ms',
                'interface_count': 24,
                'device_info': 'Cisco Catalyst (Simulated)',
                'hostname': 'SIM-SWITCH-1'
            },
            'sim_firewall_1': {
                'status': 'online',
                'last_check': datetime.now().isoformat(),
                'response_time': '30ms',
                'interface_count': 8,
                'device_info': 'Cisco ASA (Simulated)',
                'hostname': 'SIM-ASA-1'
            }
        }
        
        self.network_data['devices'] = simulated_devices
        self._add_alert("Dashboard initialized with simulated network data", 'info')
        self._update_performance_metrics()
    
    def _monitor_loop(self):
        """Monitoring loop with live/simulated mode"""
        while self.monitoring_active:
            try:
                if self.use_simulation:
                    self._update_simulated_data()
                else:
                    self._update_live_data()
                
                self._update_performance_metrics()
                self.network_data['last_update'] = datetime.now().isoformat()
                
                # Sleep interval
                sleep_time = 60 if not self.use_simulation else 30
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                # Fall back to simulation on any error
                if not self.use_simulation:
                    print("🔄 Falling back to simulation mode due to error")
                    self.use_simulation = True
                    self.network_data['mode'] = 'simulated'
                    self._setup_simulated_devices()
                time.sleep(30)
    
    def _update_live_data(self):
        """Update with real DevNet data"""
        if not self.devnet:
            return
            
        print("🔍 Checking DevNet devices...")
        
        try:
            for device_name in self.devnet.sandbox_devices.keys():
                device_status = self._check_device_status(device_name)
                self.network_data['devices'][device_name] = device_status
        except Exception as e:
            print(f"❌ Live data update failed: {e}")
            # Fall back to simulation
            self.use_simulation = True
            self.network_data['mode'] = 'simulated'
    
    def _update_simulated_data(self):
        """Update simulated data with random variations"""
        import random
        
        for device_name, device_data in self.network_data['devices'].items():
            # Simulate occasional connectivity issues
            if random.random() > 0.95:  # 5% chance of temporary issue
                device_data['status'] = 'warning'
                device_data['response_time'] = f"{random.randint(100, 300)}ms"
                self._add_alert(f"Simulated: High latency detected on {device_name}", 'warning')
            else:
                device_data['status'] = 'online'
                device_data['response_time'] = f"{random.randint(10, 50)}ms"
            
            device_data['last_check'] = datetime.now().isoformat()
    
    def _check_device_status(self, device_name: str) -> dict:
        """Check real device status"""
        if not self.devnet:
            return {'status': 'error', 'error': 'DevNet not available'}
            
        try:
            result = self.devnet.test_connectivity(device_name)
            
            if result['status'] == 'success':
                return {
                    'status': 'online',
                    'last_check': datetime.now().isoformat(),
                    'response_time': '< 100ms',
                    'device_info': result.get('device_info', {}).get('version', 'N/A'),
                    'hostname': result.get('device_info', {}).get('hostname', 'Unknown'),
                    'host': result.get('host', 'Unknown')
                }
            else:
                return {
                    'status': 'error',
                    'last_check': datetime.now().isoformat(),
                    'error': result.get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'status': 'error',
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _add_alert(self, message: str, severity: str):
        """Add alert with deduplication"""
        # Avoid duplicate alerts
        recent_messages = [a['message'] for a in self.network_data['alerts'][-3:]]
        if message not in recent_messages:
            alert = {
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'id': len(self.network_data['alerts'])
            }
            self.network_data['alerts'].append(alert)
            
            # Keep only last 10 alerts
            if len(self.network_data['alerts']) > 10:
                self.network_data['alerts'] = self.network_data['alerts'][-10:]
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        total_devices = len(self.network_data['devices'])
        online_devices = sum(1 for device in self.network_data['devices'].values() 
                           if device.get('status') == 'online')
        
        self.network_data['performance'] = {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': total_devices - online_devices,
            'uptime_percentage': round((online_devices / total_devices * 100), 1) if total_devices > 0 else 0,
            'last_updated': datetime.now().isoformat(),
            'network_health': 'Good' if online_devices == total_devices else 'Warning' if online_devices > 0 else 'Critical',
            'mode': self.network_data['mode']
        }
    
    def get_current_data(self) -> dict:
        """Get current monitoring data"""
        return self.network_data.copy()
    
    def switch_to_live_mode(self):
        """Try to switch from simulated to live mode"""
        if not self.devnet:
            return False
            
        try:
            test_results = self.devnet.test_all_devices()
            if len(test_results['working_devices']) > 0:
                print("🌐 Switching to LIVE DevNet mode")
                self.use_simulation = False
                self.network_data['mode'] = 'live'
                self._add_alert("Switched to live DevNet monitoring", 'success')
                return True
        except Exception as e:
            print(f"❌ Switch to live mode failed: {e}")
        return False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)  # Don't wait forever
        print("⏹️ Stopped network monitoring")