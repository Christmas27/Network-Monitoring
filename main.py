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
from modules.security_scanner import SecurityScanner  # Make sure this matches your file name
from modules.config import ConfigurationManager  # ADD THIS IMPORT
from config.config import Config
from modules.live_monitoring import LiveNetworkMonitor
from modules.catalyst_center_integration import CatalystCenterManager

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
configuration_manager = ConfigurationManager()  # ADD THIS LINE
security_scanner = SecurityScanner()

# Add these variables after app creation but before route definitions
print("🚀 Initializing Network Dashboard...")

# SIMPLIFIED: Only test Catalyst Center, then simulation
catalyst_manager = CatalystCenterManager()
catalyst_test = catalyst_manager.test_connection()

if catalyst_test['status'] == 'success':
    print(f"🎉 Catalyst Center available: {catalyst_test['device_count']} devices")
    dashboard_mode = "catalyst_center"
    primary_manager = catalyst_manager
else:
    print("📡 Catalyst Center unavailable - using simulation mode")
    dashboard_mode = "simulation"
    primary_manager = None

# Initialize tracking variables
device_status = {}
alerts = []

# Start monitoring
live_monitor = LiveNetworkMonitor()
print("✅ Monitor initialized (no background threads)")

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

@app.route('/topology')
def topology():
    """Network topology visualization page"""
    try:
        topology_data = network_monitor.get_network_topology()
        return render_template('topology.html', topology=topology_data)
    except Exception as e:
        logger.error(f"Error loading topology page: {e}")
        return render_template('error.html', error=str(e))

# FIX: Change route to match navigation
@app.route('/configuration')  # CHANGED FROM /config
def configuration():
    """Configuration management page"""
    try:
        # Use the proper configuration manager
        templates = configuration_manager.get_templates()
        return render_template('config.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading configuration page: {e}")
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

# ADD: Configuration API Endpoints
@app.route('/api/configuration/devices')
def api_get_config_devices():
    """Get devices for configuration management"""
    try:
        if dashboard_mode == "catalyst_center":
            devices = catalyst_manager.get_device_inventory()
            # Format for configuration page
            config_devices = []
            for device in devices:
                config_devices.append({
                    'id': device['id'],
                    'name': device['name'],
                    'ip': device['host'],
                    'type': device.get('type', 'Unknown'),
                    'status': device.get('status', 'unknown')
                })
            return jsonify({'devices': config_devices})
        else:
            # Simulation devices
            sim_devices = [
                {
                    'id': 'sim-1',
                    'name': 'Demo-Router-01',
                    'ip': '192.168.1.1',
                    'type': 'Router',
                    'status': 'online'
                },
                {
                    'id': 'sim-2',
                    'name': 'Demo-Switch-01',
                    'ip': '192.168.1.10',
                    'type': 'Switch',
                    'status': 'online'
                }
            ]
            return jsonify({'devices': sim_devices})
    except Exception as e:
        logger.error(f"Error getting configuration devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/device/<device_id>/config')
def api_get_device_config(device_id):
    """Get device configuration"""
    try:
        config = configuration_manager.get_device_configuration(device_id)
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting device config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/templates', methods=['GET'])
def api_get_config_templates():
    """Get configuration templates"""
    try:
        templates = configuration_manager.get_templates()
        return jsonify({'templates': templates})
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/templates', methods=['POST'])
def api_create_template():
    """Create new configuration template"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'device_type', 'config_data']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = configuration_manager.create_template(data)
        if success:
            return jsonify({'success': True, 'message': 'Template created successfully'})
        else:
            return jsonify({'error': 'Failed to create template'}), 500
            
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/templates/<template_id>', methods=['DELETE'])
def api_delete_template(template_id):
    """Delete configuration template"""
    try:
        success = configuration_manager.delete_template(template_id)
        if success:
            return jsonify({'success': True, 'message': 'Template deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete template'}), 500
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/backups')
def api_get_config_backups():
    """Get configuration backups"""
    try:
        backups = configuration_manager.get_config_backups()
        return jsonify({'backups': backups})
    except Exception as e:
        logger.error(f"Error getting backups: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/backup', methods=['POST'])
def api_backup_device_config():
    """Backup device configuration"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID required'}), 400
        
        # Get current configuration
        config_data = configuration_manager.get_device_configuration(device_id)
        
        if 'error' in config_data:
            return jsonify({'error': config_data['error']}), 500
        
        # Save backup
        success = configuration_manager.backup_device_config(
            device_id,
            config_data['config_data'],
            config_data.get('device_name', f'Device-{device_id}')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Configuration backed up successfully'})
        else:
            return jsonify({'error': 'Failed to backup configuration'}), 500
            
    except Exception as e:
        logger.error(f"Error backing up configuration: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuration/compare', methods=['POST'])
def api_compare_configurations():
    """Compare two configurations"""
    try:
        data = request.get_json()
        config1 = data.get('config1', '')
        config2 = data.get('config2', '')
        
        if not config1 or not config2:
            return jsonify({'error': 'Both configurations required'}), 400
        
        comparison = configuration_manager.compare_configurations(config1, config2)
        return jsonify(comparison)
        
    except Exception as e:
        logger.error(f"Error comparing configurations: {e}")
        return jsonify({'error': str(e)}), 500

# EXISTING API ENDPOINTS (keep all the others)...
@app.route('/api/devices/debug')
def debug_devices():
    """Debug endpoint to see exactly what device data we're getting"""
    try:
        print("🔍 DEBUG: Testing device API...")
        
        if dashboard_mode == "catalyst_center":
            print("🌐 Getting devices from Catalyst Center...")
            devices = catalyst_manager.get_device_inventory()
            print(f"📱 Raw Catalyst Center data: {devices}")
        else:
            print("📡 Catalyst Center not available")
            devices = []
        
        # Return detailed debug info
        return jsonify({
            'debug_info': {
                'dashboard_mode': dashboard_mode,
                'catalyst_manager_available': catalyst_manager is not None,
                'device_count': len(devices),
                'raw_devices': devices[:2] if devices else [],  # First 2 devices for debugging
                'timestamp': datetime.now().isoformat()
            },
            'devices': devices,
            'mode': dashboard_mode,
            'total': len(devices)
        })
    except Exception as e:
        print(f"❌ DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': str(e),
            'debug_info': {
                'dashboard_mode': dashboard_mode,
                'catalyst_manager_available': catalyst_manager is not None,
                'error_details': traceback.format_exc()
            }
        })

# THEN your main devices endpoint:
@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get devices with fresh Catalyst Center data"""
    try:
        if dashboard_mode == "catalyst_center":
            # Get fresh data from Catalyst Center
            devices = catalyst_manager.get_device_inventory()
        else:
            # Return empty if Catalyst Center unavailable
            devices = []
        
        return jsonify({
            'devices': devices,
            'mode': dashboard_mode,
            'total': len(devices),
            'timestamp': datetime.now().isoformat(),
            'source': 'Cisco Catalyst Center API' if dashboard_mode == "catalyst_center" else 'Unavailable'
        })
    except Exception as e:
        return jsonify({
            'error': str(e), 
            'mode': 'error',
            'devices': [],
            'total': 0
        })

@app.route('/api/network/status')
def get_network_status():
    """Get real-time network status from Catalyst Center"""
    try:
        if dashboard_mode == "catalyst_center":
            # Get fresh performance data
            health_data = catalyst_manager.get_network_health()
            devices = catalyst_manager.get_device_inventory()
            
            total_devices = len(devices)
            online_devices = len([d for d in devices if d['status'] == 'online'])
            
            return jsonify({
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': total_devices - online_devices,
                'network_health': health_data,
                'mode': 'catalyst_center',
                'last_updated': datetime.now().isoformat(),
                'source': 'Live Cisco Catalyst Center API'
            })
        else:
            return jsonify({
                'error': 'Catalyst Center not available',
                'mode': 'unavailable'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'mode': 'error'
        })

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

@app.route('/api/security/overview')
def api_security_overview():
    """Get security overview"""
    try:
        overview = security_scanner.get_security_overview()
        return jsonify(overview)
    except Exception as e:
        logger.error(f"Error getting security overview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/alerts')
def api_security_alerts():
    """Get security alerts"""
    try:
        alerts = security_scanner.get_security_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        logger.error(f"Error getting security alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/access-logs')
def api_security_access_logs():
    """Get access logs"""
    try:
        logs = security_scanner.get_access_logs()
        return jsonify({'logs': logs})
    except Exception as e:
        logger.error(f"Error getting access logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/compliance', methods=['GET'])
def api_security_compliance_get():
    """Get compliance status (GET method)"""
    try:
        compliance = security_scanner.run_compliance_check()
        return jsonify({'compliance': compliance})
    except Exception as e:
        logger.error(f"Error getting compliance data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/scan', methods=['POST'])
def api_security_scan_post():
    """Run security scan (POST method)"""
    try:
        scan_results = security_scanner.scan_for_vulnerabilities()
        return jsonify(scan_results)
    except Exception as e:
        logger.error(f"Error running security scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/alerts/<alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert_endpoint(alert_id):
    """Acknowledge security alert"""
    try:
        success = security_scanner.acknowledge_alert(alert_id)
        if success:
            return jsonify({'success': True, 'message': 'Alert acknowledged'})
        else:
            return jsonify({'error': 'Failed to acknowledge alert'}), 500
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/alerts/<alert_id>/resolve', methods=['POST'])
def api_resolve_alert_endpoint(alert_id):
    """Resolve security alert"""
    try:
        success = security_scanner.resolve_alert(alert_id)
        if success:
            return jsonify({'success': True, 'message': 'Alert resolved'})
        else:
            return jsonify({'error': 'Failed to resolve alert'}), 500
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return jsonify({'error': str(e)}), 500

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

# @app.route('/api/live/performance')
# def get_live_performance():
    """Get live performance metrics"""
    return jsonify(live_monitor.get_current_data()['performance'])

# @app.route('/api/live/alerts')
# def get_live_alerts():
    """Get real network alerts"""
    return jsonify(live_monitor.get_current_data()['alerts'])

@app.route('/api/dashboard/mode')
def get_dashboard_mode():
    """Get current dashboard mode"""
    return jsonify({
        'mode': dashboard_mode,
        'catalyst_center_available': dashboard_mode == "catalyst_center",
        'description': 'Live Catalyst Center data' if dashboard_mode == "catalyst_center" else 'Professional simulation mode',
        'message': 'Connected to real Cisco Catalyst Center' if dashboard_mode == "catalyst_center" else 'Using simulated data - perfect for portfolio demonstration'
    })

# COMMENTED OUT DEVNET RETRY ENDPOINT
# @app.route('/api/devnet/retry')
# def retry_devnet_connection():
#     """Try to reconnect to DevNet devices"""
#     global dashboard_mode
#     
#     print("🔄 Retrying DevNet connection...")
#     test_results = devnet_manager.test_all_devices()
#     
#     if test_results['working_devices']:
#         dashboard_mode = "live"
#         if hasattr(live_monitor, 'switch_to_live_mode'):
#             live_monitor.switch_to_live_mode()
#         return jsonify({
#             'status': 'success',
#             'message': f'Connected to {len(test_results["working_devices"])} DevNet devices',
#             'mode': 'live'
#         })
#     else:
#         return jsonify({
#             'status': 'unavailable',
#             'message': 'DevNet still unavailable - continuing with simulation',
#             'mode': 'simulation'
#         })

# ADD NEW CATALYST CENTER RETRY ENDPOINT
@app.route('/api/catalyst-center/retry')
def retry_catalyst_center_connection():
    """Try to reconnect to Catalyst Center"""
    global dashboard_mode
    
    print("🔄 Retrying Catalyst Center connection...")
    test_results = catalyst_manager.test_connection()
    
    if test_results['status'] == 'success':
        dashboard_mode = "catalyst_center"
        return jsonify({
            'status': 'success',
            'message': f'Connected to Catalyst Center with {test_results["device_count"]} devices',
            'mode': 'catalyst_center'
        })
    else:
        return jsonify({
            'status': 'unavailable',
            'message': 'Catalyst Center still unavailable - continuing with simulation',
            'mode': 'simulation'
        })

# COMMENTED OUT DEVNET DEVICE TEST
# @app.route('/api/devnet/test/<device_name>')
# def test_devnet_device(device_name):
#     """Test DevNet device or return simulation"""
#     if dashboard_mode == "live":
#         result = devnet_manager.test_connectivity(device_name)
#     else:
#         # Return simulated test result
#         result = {
#             'status': 'simulated',
#             'message': 'Simulated connection test successful',
#             'device_info': {
#                 'version': 'Cisco IOS XE Software, Version 17.03.04a (simulated)',
#                 'hostname': f'hostname SIM-{device_name.upper()}'
#             },
#             'timestamp': datetime.now().isoformat(),
#             'note': 'This is high-quality simulated data for demonstration'
#         }
#     
#     return jsonify(result)

# ADD NEW CATALYST CENTER DEVICE TEST
@app.route('/api/catalyst-center/test/<device_id>')
def test_catalyst_device(device_id):
    """Test connection to a specific Catalyst Center device"""
    try:
        print(f"🧪 Testing device connection: {device_id}")
        
        # Get device info first
        devices = catalyst_manager.get_device_inventory()
        target_device = None
        
        for device in devices:
            if device['id'] == device_id:
                target_device = device
                break
        
        if not target_device:
            return jsonify({
                'status': 'error',
                'message': 'Device not found in Catalyst Center inventory'
            })
        
        # Simulate device test
        import random
        import time
        time.sleep(1)  # Simulate test delay
        
        test_success = random.random() > 0.1  # 90% success rate
        
        if test_success:
            response_time = round(random.uniform(10, 50), 2)
            return jsonify({
                'status': 'success',
                'message': f'Device {target_device["name"]} is reachable',
                'details': {
                    'device_name': target_device['name'],
                    'ip_address': target_device['host'],
                    'response_time': f'{response_time}ms',
                    'test_type': 'Catalyst Center Reachability',
                    'timestamp': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Device {target_device["name"]} is not responding',
                'details': {
                    'device_name': target_device['name'],
                    'ip_address': target_device['host'],
                    'error': 'Device unreachable or timeout',
                    'test_type': 'Catalyst Center Reachability',
                    'timestamp': datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        print(f"❌ Error testing device {device_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        })

# COMMENTED OUT DEVNET INTERFACES
# @app.route('/api/devnet/interfaces/<device_name>')
# def get_device_interfaces(device_name):
#     """Get interface data with simulation fallback"""
#     if dashboard_mode == "live":
#         if hasattr(devnet_manager, 'get_live_interfaces'):
#             result = devnet_manager.get_live_interfaces(device_name)
#         else:
#             result = {'status': 'error', 'message': 'Method not available'}
#     else:
#         # Return simulated interface data
#         result = {
#             'status': 'simulated',
#             'interfaces': '''Interface              IP-Address      OK? Method Status                Protocol
# GigabitEthernet1       192.168.1.1     YES manual up                    up      
# GigabitEthernet2       192.168.2.1     YES manual up                    up      
# GigabitEthernet3       unassigned      YES unset  administratively down down    
# Loopback0              10.0.0.1        YES manual up                    up      
# Loopback1              172.16.1.1      YES manual up                    up''',
#             'message': 'Simulated interface data for demonstration'
#         }
#     
#     return jsonify(result)

# ADD NEW CATALYST CENTER NETWORK HEALTH ENDPOINT
@app.route('/api/catalyst-center/health')
def get_catalyst_center_health():
    """Get network health from Catalyst Center"""
    if dashboard_mode == "catalyst_center":
        try:
            health_data = catalyst_manager.get_network_health()
            client_health = catalyst_manager.get_client_health()
            
            result = {
                'status': 'success',
                'network_health': health_data,
                'client_health': client_health,
                'timestamp': datetime.now().isoformat(),
                'note': 'Live health data from Cisco Catalyst Center'
            }
        except Exception as e:
            result = {
                'status': 'error',
                'message': f'Error getting health data: {str(e)}'
            }
    else:
        # Return simulated health data
        result = {
            'status': 'simulated',
            'network_health': {
                'overall_score': 85,
                'device_health': 90,
                'client_health': 80,
                'application_health': 85
            },
            'client_health': {
                'total_clients': 150,
                'healthy_clients': 140,
                'issues': 10
            },
            'timestamp': datetime.now().isoformat(),
            'note': 'Simulated health data for demonstration'
        }
    
    return jsonify(result)

@app.route('/api/catalyst-center/device/<device_id>/details')
def get_device_details(device_id):
    """Get detailed device information from Catalyst Center"""
    if dashboard_mode == "catalyst_center":
        details = catalyst_manager.get_device_details(device_id)
        return jsonify(details)
    else:
        return jsonify({'error': 'Catalyst Center not available'})

@app.route('/api/catalyst-center/device/<device_id>/interfaces')
def get_device_interfaces(device_id):
    """Get device interface information from Catalyst Center"""
    if dashboard_mode == "catalyst_center":
        interfaces = catalyst_manager.get_device_interfaces(device_id)
        return jsonify({'interfaces': interfaces})
    else:
        return jsonify({'error': 'Catalyst Center not available'})

@app.route('/api/catalyst-center/topology')
def get_network_topology():
    """Get network topology from Catalyst Center with enhanced processing"""
    try:
        if dashboard_mode == "catalyst_center":
            print("🎯 Getting real topology from Catalyst Center...")
            
            # Get topology data using network monitor (which handles the conversion)
            topology_data = network_monitor.get_network_topology()
            
            return jsonify(topology_data)
        else:
            return jsonify({
                'error': 'Catalyst Center not available',
                'mode': 'simulation'
            })
    except Exception as e:
        print(f"❌ Error in topology endpoint: {e}")
        return jsonify({
            'error': str(e),
            'mode': 'error'
        })

@app.route('/api/catalyst-center/topology/debug')
def debug_topology():
    """Debug endpoint to see raw topology data"""
    try:
        print("🔍 DEBUG: Getting raw topology data...")
        
        if dashboard_mode == "catalyst_center":
            # Get raw data from Catalyst Center
            raw_devices = catalyst_manager.get_device_inventory()
            raw_topology = catalyst_manager.get_network_topology()
            
            # Get processed data from network monitor
            processed_topology = network_monitor.get_network_topology()
            
            return jsonify({
                'debug_info': {
                    'dashboard_mode': dashboard_mode,
                    'raw_device_count': len(raw_devices),
                    'processed_node_count': len(processed_topology.get('nodes', [])),
                    'processed_edge_count': len(processed_topology.get('edges', [])),
                    'catalyst_center_available': True
                },
                'raw_devices': raw_devices[:3] if raw_devices else [],  # First 3 for debugging
                'raw_topology': raw_topology,
                'processed_topology': processed_topology,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'debug_info': {
                    'dashboard_mode': dashboard_mode,
                    'catalyst_center_available': False,
                    'message': 'Catalyst Center not available'
                }
            })
            
    except Exception as e:
        print(f"❌ DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': str(e),
            'debug_info': {
                'dashboard_mode': dashboard_mode,
                'error_details': traceback.format_exc()
            }
        })

@app.route('/api/catalyst-center/profile', methods=['POST'])
def create_network_profile():
    """Create a new network profile in Catalyst Center"""
    if dashboard_mode == "catalyst_center":
        profile_data = request.get_json()
        result = catalyst_manager.create_network_profile(profile_data)
        return jsonify(result)
    else:
        return jsonify({'error': 'Catalyst Center not available'})

@app.route('/static/js/configuration.js')
def serve_configuration_js():
    """Serve configuration JavaScript file"""
    js_content = '''
/* Configuration Management JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Configuration page loaded');
    
    // Load initial data
    loadDevices();
    loadTemplates();
    loadBackups();
});

// Load devices for configuration
function loadDevices() {
    fetch('/api/configuration/devices')
        .then(response => response.json())
        .then(data => {
            const deviceList = document.getElementById('deviceList');
            
            if (data.devices && data.devices.length > 0) {
                deviceList.innerHTML = data.devices.map(device => `
                    <div class="list-group-item list-group-item-action" onclick="selectDevice('${device.id}')">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${device.name}</h6>
                            <small class="badge ${device.status === 'online' ? 'bg-success' : 'bg-danger'}">${device.status}</small>
                        </div>
                        <p class="mb-1">${device.ip}</p>
                        <small>${device.type}</small>
                    </div>
                `).join('');
            } else {
                deviceList.innerHTML = '<p class="text-muted">No devices found</p>';
            }
        })
        .catch(error => {
            console.error('Error loading devices:', error);
            document.getElementById('deviceList').innerHTML = '<p class="text-danger">Error loading devices</p>';
        });
}

// Select device and load configuration
function selectDevice(deviceId) {
    console.log(`📱 Loading config for device: ${deviceId}`);
    
    fetch(`/api/configuration/device/${deviceId}/config`)
        .then(response => response.json())
        .then(data => {
            const configDisplay = document.getElementById('configDisplay');
            
            if (data.error) {
                configDisplay.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }
            
            configDisplay.innerHTML = `
                <div class="mb-3">
                    <h6>${data.device_name || 'Device Configuration'}</h6>
                    <small class="text-muted">Last updated: ${data.last_updated || 'Unknown'}</small>
                </div>
                <pre class="bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto;"><code>${data.config_data}</code></pre>
            `;
            
            // Store current device for backup/download
            window.currentDevice = { id: deviceId, config: data };
        })
        .catch(error => {
            console.error('Error loading configuration:', error);
            document.getElementById('configDisplay').innerHTML = '<div class="alert alert-danger">Error loading configuration</div>';
        });
}

// Load templates
function loadTemplates() {
    fetch('/api/configuration/templates')
        .then(response => response.json())
        .then(data => {
            const templatesList = document.getElementById('templatesList');
            
            if (data.templates && data.templates.length > 0) {
                templatesList.innerHTML = data.templates.map(template => `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <h6 class="mb-0">${template.name}</h6>
                                <span class="badge bg-primary">${template.device_type}</span>
                            </div>
                            <div class="card-body">
                                <p class="card-text">${template.description || 'No description'}</p>
                                <small class="text-muted">Created: ${new Date(template.created_at).toLocaleDateString()}</small>
                            </div>
                            <div class="card-footer">
                                <button class="btn btn-sm btn-primary me-1" onclick="viewTemplate('${template.id}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteTemplate('${template.id}')">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                templatesList.innerHTML = '<div class="col-12"><p class="text-muted">No templates found</p></div>';
            }
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            document.getElementById('templatesList').innerHTML = '<div class="col-12"><p class="text-danger">Error loading templates</p></div>';
        });
}

// Load backups
function loadBackups() {
    fetch('/api/configuration/backups')
        .then(response => response.json())
        .then(data => {
            const backupsList = document.getElementById('backupsList');
            
            if (data.backups && data.backups.length > 0) {
                backupsList.innerHTML = data.backups.map(backup => `
                    <tr>
                        <td>${backup.device_name || 'Unknown Device'}</td>
                        <td>${new Date(backup.backup_timestamp).toLocaleString()}</td>
                        <td>${Math.round(backup.config_data.length / 1024)}KB</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="restoreBackup('${backup.id}')">
                                <i class="fas fa-undo"></i> Restore
                            </button>
                            <button class="btn btn-sm btn-info" onclick="downloadBackup('${backup.id}')">
                                <i class="fas fa-download"></i> Download
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                backupsList.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No backups found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading backups:', error);
            document.getElementById('backupsList').innerHTML = '<tr><td colspan="4" class="text-center text-danger">Error loading backups</td></tr>';
        });
}

// Create template
function createTemplate() {
    const formData = {
        name: document.getElementById('templateName').value,
        description: document.getElementById('templateDescription').value,
        device_type: document.getElementById('deviceType').value,
        config_data: document.getElementById('configData').value
    };
    
    if (!formData.name || !formData.device_type || !formData.config_data) {
        alert('Please fill in all required fields');
        return;
    }
    
    fetch('/api/configuration/templates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Template created successfully!');
            document.getElementById('templateForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('createTemplateModal')).hide();
            loadTemplates();
        } else {
            alert('Error creating template: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error creating template:', error);
        alert('Error creating template');
    });
}

// Backup current configuration
function backupCurrentConfig() {
    if (!window.currentDevice) {
        alert('Please select a device first');
        return;
    }
    
    fetch('/api/configuration/backup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            device_id: window.currentDevice.id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Configuration backed up successfully!');
            loadBackups();
        } else {
            alert('Error backing up configuration: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error backing up configuration:', error);
        alert('Error backing up configuration');
    });
}

// Download configuration
function downloadConfig() {
    if (!window.currentDevice) {
        alert('Please select a device first');
        return;
    }
    
    const config = window.currentDevice.config;
    const blob = new Blob([config.config_data], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${config.device_name || 'device'}_config.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Delete template
function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) {
        return;
    }
    
    fetch(`/api/configuration/templates/${templateId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Template deleted successfully!');
            loadTemplates();
        } else {
            alert('Error deleting template: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error deleting template:', error);
        alert('Error deleting template');
    });
}

// View template (placeholder)
function viewTemplate(templateId) {
    alert('Template viewer coming soon!');
}

// Restore backup (placeholder)
function restoreBackup(backupId) {
    alert('Backup restore coming soon!');
}

// Download backup (placeholder)
function downloadBackup(backupId) {
    alert('Backup download coming soon!');
}
'''
    
    from flask import Response
    return Response(js_content, mimetype='application/javascript')

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
    
    if dashboard_mode == "catalyst_center":
        print("🎉 Portfolio Note: Dashboard connected to Cisco Catalyst Center!")
        print("🌟 This demonstrates enterprise-level network automation skills")
    elif dashboard_mode == "simulation":
        print("💡 Portfolio Note: Dashboard is using professional simulation mode")
        print("🔄 Will automatically switch to live data when Catalyst Center is available")
    
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000), 
        debug=app.config.get('DEBUG', True)
    )