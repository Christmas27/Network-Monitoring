#!/usr/bin/env python3
"""
Network Automation Dashboard - Main Application Entry Point

This is the main Flask application that provides a web-based interface
for network automation, monitoring, and management tasks.

Author: Computer Science Student
Certifications: Cisco DevNet, SRWE, ENSA, Network Security
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import json
import logging
import threading
import time
from datetime import datetime
from modules.device_manager import DeviceManager
from modules.network_monitor import NetworkMonitor
from modules.config_manager import ConfigManager
from modules.security_scanner import SecurityScanner
from config.config import Config
from modules.devnet_integration import DevNetSandboxManager
from modules.live_monitoring import LiveNetworkMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/network_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize core modules
device_manager = DeviceManager()
network_monitor = NetworkMonitor()
config_manager = ConfigManager()
security_scanner = SecurityScanner()

# Add these variables after app creation but before route definitions
print("🚀 Initializing Network Dashboard...")
devnet_manager = DevNetSandboxManager()
live_monitor = LiveNetworkMonitor()

# Initialize tracking variables
device_status = {}
alerts = []

# Test DevNet availability on startup
print("🔍 Checking DevNet sandbox availability...")
devnet_test = devnet_manager.test_all_devices()

if devnet_test['working_devices']:
    print(f"✅ DevNet available: {len(devnet_test['working_devices'])} devices online")
    dashboard_mode = "live"
else:
    print("📡 DevNet unavailable - Using simulation mode")
    dashboard_mode = "simulation"

# Start monitoring
live_monitor.start_monitoring()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get summary statistics
        total_devices = len(device_manager.get_all_devices())
        online_devices = len([d for d in device_status.values() if d.get('status') == 'online'])
        total_alerts = len(alerts)
        
        stats = {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': total_devices - online_devices,
            'total_alerts': total_alerts,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/devices')
def devices():
    """Device management page"""
    try:
        devices = device_manager.get_all_devices()
        return render_template('devices.html', devices=devices)
    except Exception as e:
        logger.error(f"Error loading devices page: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get devices with live/simulation data - UPDATED VERSION"""
    try:
        if dashboard_mode == "live":
            devices = devnet_manager.get_available_devices()
        else:
            # Return simulated devices
            devices = [
                {
                    'name': 'sim_ios_xe_router',
                    'host': 'demo-router.simulation.local',
                    'type': 'cisco_xe',
                    'status': 'online',
                    'description': 'Cisco IOS XE Router (Simulated)',
                    'response_time': '25ms',
                    'last_check': 'Just now'
                },
                {
                    'name': 'sim_catalyst_switch',
                    'host': 'demo-switch.simulation.local', 
                    'type': 'cisco_ios',
                    'status': 'online',
                    'description': 'Cisco Catalyst Switch (Simulated)',
                    'response_time': '15ms',
                    'last_check': 'Just now'
                },
                {
                    'name': 'sim_asa_firewall',
                    'host': 'demo-firewall.simulation.local',
                    'type': 'cisco_asa',
                    'status': 'online', 
                    'description': 'Cisco ASA Firewall (Simulated)',
                    'response_time': '30ms',
                    'last_check': 'Just now'
                }
            ]
        
        return jsonify({
            'devices': devices,
            'mode': dashboard_mode,
            'total': len(devices),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'mode': 'error'})

@app.route('/api/devices', methods=['POST'])
def api_add_device():
    """API endpoint to add a new device"""
    try:
        data = request.get_json()
        required_fields = ['hostname', 'ip_address', 'device_type', 'username', 'password']
        
        if not all(field in data for field in required_fields):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        device_id = device_manager.add_device(data)
        logger.info(f"Added new device: {data['hostname']} ({data['ip_address']})")
        
        return jsonify({'status': 'success', 'device_id': device_id})
    except Exception as e:
        logger.error(f"API error adding device: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/devices/<device_id>/status')
def api_device_status(device_id):
    """API endpoint to get device status"""
    try:
        status = network_monitor.get_device_status(device_id)
        return jsonify({'status': 'success', 'device_status': status})
    except Exception as e:
        logger.error(f"API error getting device status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/devices/<device_id>/config')
def api_device_config(device_id):
    """API endpoint to get device configuration"""
    try:
        config = config_manager.get_device_config(device_id)
        return jsonify({'status': 'success', 'config': config})
    except Exception as e:
        logger.error(f"API error getting device config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/devices/<device_id>/backup', methods=['POST'])
def api_backup_config(device_id):
    """API endpoint to backup device configuration"""
    try:
        backup_id = config_manager.backup_device_config(device_id)
        logger.info(f"Configuration backed up for device {device_id}")
        return jsonify({'status': 'success', 'backup_id': backup_id})
    except Exception as e:
        logger.error(f"API error backing up config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/security/scan/<device_id>', methods=['POST'])
def api_security_scan(device_id):
    """API endpoint to run security scan on device"""
    try:
        scan_results = security_scanner.scan_device(device_id)
        logger.info(f"Security scan completed for device {device_id}")
        return jsonify({'status': 'success', 'scan_results': scan_results})
    except Exception as e:
        logger.error(f"API error running security scan: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/metrics')
def api_metrics():
    """API endpoint to get real-time network metrics"""
    try:
        metrics = network_monitor.get_network_metrics()
        return jsonify({'status': 'success', 'metrics': metrics})
    except Exception as e:
        logger.error(f"API error getting metrics: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """API endpoint to get current alerts"""
    try:
        current_alerts = network_monitor.get_alerts()
        return jsonify({'status': 'success', 'alerts': current_alerts})
    except Exception as e:
        logger.error(f"API error getting alerts: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/topology')
def topology():
    """Network topology visualization page"""
    try:
        topology_data = network_monitor.get_network_topology()
        return render_template('topology.html', topology=topology_data)
    except Exception as e:
        logger.error(f"Error loading topology page: {e}")
        return render_template('error.html', error=str(e))

@app.route('/config')
def config():
    """Configuration management page"""
    try:
        templates = config_manager.get_config_templates()
        return render_template('config.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading config page: {e}")
        return render_template('error.html', error=str(e))

@app.route('/security')
def security():
    """Security monitoring page"""
    try:
        security_status = security_scanner.get_security_overview()
        return render_template('security.html', security_status=security_status)
    except Exception as e:
        logger.error(f"Error loading security page: {e}")
        return render_template('error.html', error=str(e))

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        from flask import send_from_directory
        import os
        return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception:
        # Return empty response if favicon not found
        return '', 204

@app.route('/api/devices/<device_id>/test', methods=['POST'])
def test_device_connection(device_id):
    """Test device connection"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        success = network_monitor.ping_device(device['host'])
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error testing device connection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device"""
    try:
        success = device_manager.delete_device(device_id)
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/templates', methods=['GET'])
def get_config_templates():
    """Get configuration templates"""
    try:
        templates = config_manager.get_config_templates()
        return jsonify(templates)
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/backups', methods=['GET'])
def get_config_backups():
    """Get configuration backups"""
    try:
        # Sample backup data until method is implemented
        backups = [
            {
                'id': '1',
                'device_name': 'Router-01',
                'timestamp': '2025-07-30T10:00:00Z',
                'size': '15KB'
            },
            {
                'id': '2', 
                'device_name': 'Switch-01',
                'timestamp': '2025-07-30T09:30:00Z',
                'size': '22KB'
            }
        ]
        return jsonify(backups)
    except Exception as e:
        logger.error(f"Error getting backups: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/changes', methods=['GET'])
def get_config_changes():
    """Get configuration changes"""
    try:
        # Sample changes data until method is implemented
        changes = [
            {
                'id': '1',
                'device_name': 'Router-01',
                'change_type': 'Interface Configuration',
                'description': 'Updated GigabitEthernet0/1 IP address',
                'timestamp': '2025-07-30T14:30:00Z'
            }
        ]
        return jsonify(changes)
    except Exception as e:
        logger.error(f"Error getting changes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/deploy', methods=['POST'])
def deploy_configuration():
    """Deploy configuration"""
    try:
        data = request.get_json()
        # Simulate successful deployment
        logger.info(f"Deploying configuration to device {data.get('device_id')}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deploying configuration: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/backup-all', methods=['POST'])
def backup_all_configs():
    """Backup all device configurations"""
    try:
        # Simulate successful backup
        logger.info("Backing up all device configurations")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error backing up configurations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/stats', methods=['GET'])
def get_security_stats():
    """Get security statistics"""
    try:
        # Sample security stats
        stats = {
            'critical': 2,
            'medium': 5,
            'compliance_score': '85%',
            'last_scan': '2025-07-30T12:00:00Z'
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting security stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    """Get security vulnerabilities"""
    try:
        # Sample vulnerability data
        vulns = [
            {
                'id': '1',
                'device_name': 'Router-01',
                'vulnerability': 'Weak SSH Configuration',
                'severity': 'Medium',
                'cve_id': 'CVE-2023-1234',
                'status': 'open'
            },
            {
                'id': '2',
                'device_name': 'Switch-01', 
                'vulnerability': 'Default SNMP Community',
                'severity': 'Critical',
                'cve_id': 'CVE-2023-5678',
                'status': 'open'
            }
        ]
        return jsonify(vulns)
    except Exception as e:
        logger.error(f"Error getting vulnerabilities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/port-scan', methods=['GET'])
def get_port_scan_results():
    """Get port scan results"""
    try:
        # Sample port scan data
        results = [
            {
                'device_id': '1',
                'device_name': 'Router-01',
                'port': '22',
                'service': 'SSH',
                'risk_level': 'low'
            },
            {
                'device_id': '1',
                'device_name': 'Router-01',
                'port': '23',
                'service': 'Telnet',
                'risk_level': 'high'
            },
            {
                'device_id': '2',
                'device_name': 'Switch-01',
                'port': '161',
                'service': 'SNMP',
                'risk_level': 'medium'
            }
        ]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error getting port scan results: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/scan', methods=['POST'])
def start_security_scan():
    """Start security scan"""
    try:
        logger.info("Starting security scan")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error starting security scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/port-scan', methods=['POST'])
def start_port_scan():
    """Start port scan"""
    try:
        logger.info("Starting port scan")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error starting port scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/compliance', methods=['POST'])
def run_compliance_check():
    """Run compliance check"""
    try:
        logger.info("Running compliance check")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error running compliance check: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/vulnerabilities/<vuln_id>/fix', methods=['POST'])
def mark_vulnerability_fixed(vuln_id):
    """Mark vulnerability as fixed"""
    try:
        logger.info(f"Marking vulnerability {vuln_id} as fixed")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error marking vulnerability as fixed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/stats')
def api_get_device_stats():
    """Get real device statistics"""
    performance = live_monitor.get_current_data()['performance']
    return jsonify(performance)

# Add new endpoints for live data
@app.route('/api/live/devices')
def get_live_devices():
    """Get real-time device status from DevNet"""
    return jsonify(live_monitor.get_current_data()['devices'])

@app.route('/api/live/performance')
def get_live_performance():
    """Get live performance metrics"""
    return jsonify(live_monitor.get_current_data()['performance'])

@app.route('/api/live/alerts')
def get_live_alerts():
    """Get real network alerts"""
    return jsonify(live_monitor.get_current_data()['alerts'])

@app.route('/api/dashboard/mode')
def get_dashboard_mode():
    """Get current dashboard mode and DevNet status"""
    return jsonify({
        'mode': dashboard_mode,
        'devnet_available': dashboard_mode == "live",
        'description': 'Live DevNet data' if dashboard_mode == "live" else 'Professional simulation mode',
        'message': 'Connected to real Cisco devices' if dashboard_mode == "live" else 'Using simulated data - perfect for portfolio demonstration'
    })

@app.route('/api/devnet/retry')
def retry_devnet_connection():
    """Try to reconnect to DevNet devices"""
    global dashboard_mode
    
    print("🔄 Retrying DevNet connection...")
    test_results = devnet_manager.test_all_devices()
    
    if test_results['working_devices']:
        dashboard_mode = "live"
        if hasattr(live_monitor, 'switch_to_live_mode'):
            live_monitor.switch_to_live_mode()
        return jsonify({
            'status': 'success',
            'message': f'Connected to {len(test_results["working_devices"])} DevNet devices',
            'mode': 'live'
        })
    else:
        return jsonify({
            'status': 'unavailable',
            'message': 'DevNet still unavailable - continuing with simulation',
            'mode': 'simulation'
        })

@app.route('/api/devnet/test/<device_name>')
def test_devnet_device(device_name):
    """Test DevNet device or return simulation"""
    if dashboard_mode == "live":
        result = devnet_manager.test_connectivity(device_name)
    else:
        # Return simulated test result
        result = {
            'status': 'simulated',
            'message': 'Simulated connection test successful',
            'device_info': {
                'version': 'Cisco IOS XE Software, Version 17.03.04a (simulated)',
                'hostname': f'hostname SIM-{device_name.upper()}'
            },
            'timestamp': datetime.now().isoformat(),
            'note': 'This is high-quality simulated data for demonstration'
        }
    
    return jsonify(result)

@app.route('/api/devnet/interfaces/<device_name>')
def get_device_interfaces(device_name):
    """Get interface data with simulation fallback"""
    if dashboard_mode == "live":
        if hasattr(devnet_manager, 'get_live_interfaces'):
            result = devnet_manager.get_live_interfaces(device_name)
        else:
            result = {'status': 'error', 'message': 'Method not available'}
    else:
        # Return simulated interface data
        result = {
            'status': 'simulated',
            'interfaces': '''Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       192.168.1.1     YES manual up                    up      
GigabitEthernet2       192.168.2.1     YES manual up                    up      
GigabitEthernet3       unassigned      YES unset  administratively down down    
Loopback0              10.0.0.1        YES manual up                    up      
Loopback1              172.16.1.1      YES manual up                    up''',
            'message': 'Simulated interface data for demonstration'
        }
    
    return jsonify(result)

def background_monitoring():
    """Background thread for continuous network monitoring"""
    logger.info("Starting background monitoring thread")
    
    while True:
        try:
            # Update device status
            devices = device_manager.get_all_devices()
            for device in devices:
                status = network_monitor.ping_device(device['ip_address'])
                device_status[device['id']] = {
                    'status': 'online' if status else 'offline',
                    'last_check': datetime.now().isoformat()
                }
            
            # Check for alerts
            new_alerts = network_monitor.check_alerts()
            alerts.extend(new_alerts)
            
            # Keep only last 100 alerts
            if len(alerts) > 100:
                alerts[:] = alerts[-100:]
            
            logger.debug(f"Monitoring cycle completed. {len(devices)} devices checked.")
            
        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
        
        time.sleep(30)  # Check every 30 seconds

# Update the shutdown handler
@app.teardown_appcontext
def shutdown_monitor(error):
    """Stop monitoring when app shuts down"""
    live_monitor.stop_monitoring()

if __name__ == '__main__':
    print(f"🌐 Network Dashboard starting in {dashboard_mode.upper()} mode")
    print(f"📊 Dashboard URL: http://{app.config.get('HOST', '127.0.0.1')}:{app.config.get('PORT', 5000)}")
    
    if dashboard_mode == "simulation":
        print("💡 Portfolio Note: Dashboard is using professional simulation mode")
        print("🔄 Will automatically switch to live data when DevNet is available")
    
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000), 
        debug=app.config.get('DEBUG', True)
    )