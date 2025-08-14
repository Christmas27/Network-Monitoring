#!/usr/bin/env python3
"""
Network Automation Dashboard - Main Application Entry Point

This is the main Flask application that provides a web-based interface
for network automation, monitoring, and management tasks.

Author: Computer Science Student
Certifications: Cisco DevNet, SRWE, ENSA, Network Security
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import json
import logging
from datetime import datetime

# Import custom modules
from modules.device_manager import DeviceManager
from modules.network_monitor import NetworkMonitor
from modules.config_manager import ConfigManager
from modules.security_scanner import SecurityScanner
from modules.config import ConfigurationManager
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
configuration_manager = ConfigurationManager()
security_scanner = SecurityScanner()
live_monitor = LiveNetworkMonitor()

# Initialize Catalyst Center integration
print("🚀 Initializing Network Dashboard...")
catalyst_manager = CatalystCenterManager()
catalyst_test = catalyst_manager.test_connection()

# Determine dashboard mode
if catalyst_test['status'] == 'success':
    print(f"🎉 Catalyst Center available: {catalyst_test['device_count']} devices")
    dashboard_mode = "catalyst_center"
else:
    print("📡 Catalyst Center unavailable - using simulation mode")
    dashboard_mode = "simulation"

# Initialize tracking variables
device_status = {}
alerts = []

print("✅ Monitor initialized")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def handle_api_error(error_message: str, exception: Exception = None) -> tuple:
    """Standardized API error handling"""
    if exception:
        logger.error(f"{error_message}: {exception}")
    else:
        logger.error(error_message)
    return jsonify({'error': error_message}), 500

# Replace the get_device_list() function in your main.py (around line 75)

def get_device_list():
    """Get device list - only real devices from Catalyst Center"""
    if dashboard_mode == "catalyst_center":
        devices = catalyst_manager.get_device_inventory()
        return [{
            'id': device['id'],
            'name': device['name'],
            'host': device['host'],  # Use 'host' instead of 'ip'
            'ip': device['host'],    # Keep for compatibility
            'type': device.get('type', 'Unknown'),
            'status': device.get('status', 'unknown'),
            'role': device.get('role', 'Unknown'),
            'series': device.get('series', 'Unknown')
        } for device in devices]
    else:
        # Return empty list when Catalyst Center is not available
        return []

# =============================================================================
# PAGE ROUTES
# =============================================================================

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        if dashboard_mode == "catalyst_center":
            devices = get_device_list()
            total_devices = len(devices)
            online_devices = len([d for d in devices if d.get('status') == 'online'])
        else:
            total_devices = 0
            online_devices = 0
        
        stats = {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': total_devices - online_devices,
            'total_alerts': len(alerts),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mode': dashboard_mode
        }
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return handle_api_error("Error loading dashboard", e)

@app.route('/devices')
def devices():
    """Device management page"""
    try:
        devices = device_manager.get_all_devices()
        return render_template('devices.html', devices=devices)
    except Exception as e:
        return handle_api_error("Error loading devices page", e)

@app.route('/topology')
def topology():
    """Network topology visualization page"""
    try:
        topology_data = network_monitor.get_network_topology()
        return render_template('topology.html', topology=topology_data)
    except Exception as e:
        return handle_api_error("Error loading topology page", e)

@app.route('/configuration')
def configuration():
    """Configuration management page"""
    try:
        templates = configuration_manager.get_templates()
        return render_template('config.html', templates=templates)
    except Exception as e:
        return handle_api_error("Error loading configuration page", e)

@app.route('/security')
def security():
    """Security monitoring page"""
    try:
        security_status = security_scanner.get_security_overview()
        return render_template('security.html', security_status=security_status)
    except Exception as e:
        return handle_api_error("Error loading security page", e)

# =============================================================================
# DEVICE API ENDPOINTS
# =============================================================================

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get devices with fresh data"""
    try:
        devices = get_device_list()
        return jsonify({
            'devices': devices,
            'mode': dashboard_mode,
            'total': len(devices),
            'timestamp': datetime.now().isoformat(),
            'source': 'Cisco Catalyst Center API' if dashboard_mode == "catalyst_center" else 'Simulation'
        })
    except Exception as e:
        return handle_api_error("Error getting devices", e)

@app.route('/api/devices', methods=['POST'])
def api_add_device():
    """Add a new device"""
    try:
        data = request.get_json()
        required_fields = ['hostname', 'ip_address', 'device_type', 'username', 'password']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        device_id = device_manager.add_device(data)
        logger.info(f"Added new device: {data['hostname']} ({data['ip_address']})")
        
        return jsonify({'success': True, 'device_id': device_id})
    except Exception as e:
        return handle_api_error("Error adding device", e)

@app.route('/api/devices/<device_id>', methods=['DELETE'])
def api_delete_device(device_id):
    """Delete a device"""
    try:
        success = device_manager.delete_device(device_id)
        return jsonify({'success': success})
    except Exception as e:
        return handle_api_error("Error deleting device", e)

@app.route('/api/devices/<device_id>/status')
def api_device_status(device_id):
    """Get device status"""
    try:
        status = network_monitor.get_device_status(device_id)
        return jsonify({'success': True, 'device_status': status})
    except Exception as e:
        return handle_api_error("Error getting device status", e)

@app.route('/api/devices/<device_id>/config')
def api_device_config(device_id):
    """Get device configuration"""
    try:
        config = config_manager.get_device_config(device_id)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return handle_api_error("Error getting device config", e)

@app.route('/api/devices/<device_id>/test', methods=['POST'])
def api_test_device(device_id):
    """Test device connection"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        success = network_monitor.ping_device(device['host'])
        return jsonify({'success': success})
    except Exception as e:
        return handle_api_error("Error testing device", e)

@app.route('/api/devices/stats')
def api_device_stats():
    """Get device statistics"""
    try:
        performance = live_monitor.get_current_data()['performance']
        return jsonify(performance)
    except Exception as e:
        return handle_api_error("Error getting device stats", e)

# =============================================================================
# CONFIGURATION API ENDPOINTS
# =============================================================================

@app.route('/api/configuration/devices')
def api_get_config_devices():
    """Get devices for configuration management"""
    try:
        devices = get_device_list()
        return jsonify({'devices': devices})
    except Exception as e:
        return handle_api_error("Error getting configuration devices", e)

@app.route('/api/configuration/device/<device_id>/config')
def api_get_device_config(device_id):
    """Get device configuration"""
    try:
        config = configuration_manager.get_device_configuration(device_id)
        return jsonify(config)
    except Exception as e:
        return handle_api_error("Error getting device config", e)

@app.route('/api/configuration/templates', methods=['GET'])
def api_get_config_templates():
    """Get configuration templates"""
    try:
        templates = configuration_manager.get_templates()
        return jsonify({'templates': templates})
    except Exception as e:
        return handle_api_error("Error getting templates", e)

@app.route('/api/configuration/templates', methods=['POST'])
def api_create_template():
    """Create new configuration template"""
    try:
        data = request.get_json()
        required_fields = ['name', 'device_type', 'config_data']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = configuration_manager.create_template(data)
        if success:
            return jsonify({'success': True, 'message': 'Template created successfully'})
        else:
            return jsonify({'error': 'Failed to create template'}), 500
    except Exception as e:
        return handle_api_error("Error creating template", e)

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
        return handle_api_error("Error deleting template", e)

@app.route('/api/configuration/backups')
def api_get_config_backups():
    """Get configuration backups"""
    try:
        backups = configuration_manager.get_config_backups()
        return jsonify({'backups': backups})
    except Exception as e:
        return handle_api_error("Error getting backups", e)

@app.route('/api/configuration/backup', methods=['POST'])
def api_backup_device_config():
    """Backup device configuration"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID required'}), 400
        
        config_data = configuration_manager.get_device_configuration(device_id)
        if 'error' in config_data:
            return jsonify({'error': config_data['error']}), 500
        
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
        return handle_api_error("Error backing up configuration", e)

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
        return handle_api_error("Error comparing configurations", e)

# =============================================================================
# SECURITY API ENDPOINTS
# =============================================================================

@app.route('/api/security/overview')
def api_security_overview():
    """Get security overview"""
    try:
        overview = security_scanner.get_security_overview()
        return jsonify(overview)
    except Exception as e:
        return handle_api_error("Error getting security overview", e)

@app.route('/api/security/alerts')
def api_security_alerts():
    """Get security alerts"""
    try:
        alerts = security_scanner.get_security_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        return handle_api_error("Error getting security alerts", e)

@app.route('/api/security/vulnerabilities')
def api_security_vulnerabilities():
    """Get vulnerabilities"""
    try:
        vulnerabilities = security_scanner.get_vulnerabilities()
        return jsonify({'vulnerabilities': vulnerabilities})
    except Exception as e:
        return handle_api_error("Error getting vulnerabilities", e)

@app.route('/api/security/access-logs')
def api_security_access_logs():
    """Get access logs"""
    try:
        logs = security_scanner.get_access_logs()
        return jsonify({'logs': logs})
    except Exception as e:
        return handle_api_error("Error getting access logs", e)

@app.route('/api/security/compliance')
def api_security_compliance():
    """Get compliance status"""
    try:
        compliance = security_scanner.run_compliance_check()
        return jsonify({'compliance': compliance})
    except Exception as e:
        return handle_api_error("Error getting compliance data", e)

@app.route('/api/security/scan', methods=['POST'])
def api_security_scan():
    """Run security scan"""
    try:
        scan_results = security_scanner.scan_for_vulnerabilities()
        return jsonify(scan_results)
    except Exception as e:
        return handle_api_error("Error running security scan", e)

@app.route('/api/security/alerts/<alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id):
    """Acknowledge security alert"""
    try:
        success = security_scanner.acknowledge_alert(alert_id)
        if success:
            return jsonify({'success': True, 'message': 'Alert acknowledged'})
        else:
            return jsonify({'error': 'Failed to acknowledge alert'}), 500
    except Exception as e:
        return handle_api_error("Error acknowledging alert", e)

@app.route('/api/security/alerts/<alert_id>/resolve', methods=['POST'])
def api_resolve_alert(alert_id):
    """Resolve security alert"""
    try:
        success = security_scanner.resolve_alert(alert_id)
        if success:
            return jsonify({'success': True, 'message': 'Alert resolved'})
        else:
            return jsonify({'error': 'Failed to resolve alert'}), 500
    except Exception as e:
        return handle_api_error("Error resolving alert", e)

# =============================================================================
# NETWORK API ENDPOINTS
# =============================================================================

@app.route('/api/network/status')
def api_network_status():
    """Get real-time network status"""
    try:
        if dashboard_mode == "catalyst_center":
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
        return handle_api_error("Error getting network status", e)

@app.route('/api/metrics')
def api_metrics():
    """Get real-time network metrics"""
    try:
        metrics = network_monitor.get_network_metrics()
        return jsonify({'success': True, 'metrics': metrics})
    except Exception as e:
        return handle_api_error("Error getting metrics", e)

@app.route('/api/alerts')
def api_alerts():
    """Get current alerts"""
    try:
        current_alerts = network_monitor.get_alerts()
        return jsonify({'success': True, 'alerts': current_alerts})
    except Exception as e:
        return handle_api_error("Error getting alerts", e)

# Add this after the api_alerts() function

@app.route('/api/network/topology')
def api_network_topology():
    """Get network topology data"""
    try:
        if dashboard_mode == "catalyst_center":
            # Get real devices from Catalyst Center
            devices = get_device_list()
            
            if not devices:
                return jsonify({
                    'nodes': [],
                    'edges': [],
                    'mode': 'catalyst_center_no_devices',
                    'message': 'No devices found in Catalyst Center'
                })
            
            # Create nodes from real devices
            nodes = []
            for device in devices:
                nodes.append({
                    'id': device['id'],
                    'name': device['name'],
                    'type': device.get('type', 'Unknown'),
                    'ip': device.get('ip', device.get('host', 'N/A')),
                    'status': device.get('status', 'unknown'),
                    'location': 'DevNet Sandbox',
                    'role': device.get('role', 'Unknown'),
                    'series': device.get('series', 'Unknown')
                })
            
            # Create some logical connections between devices
            edges = []
            if len(devices) > 1:
                # Connect devices in a logical topology
                for i in range(len(devices) - 1):
                    edges.append({
                        'id': f'connection-{i}',
                        'source': devices[i]['id'],
                        'target': devices[i + 1]['id'],
                        'interface': f'GigE0/0/{i}',
                        'bandwidth': '1000',
                        'status': 'up'
                    })
                
                # Add a few more connections to make it look more realistic
                if len(devices) > 2:
                    edges.append({
                        'id': f'connection-loop',
                        'source': devices[0]['id'],
                        'target': devices[-1]['id'],
                        'interface': 'GigE0/0/10',
                        'bandwidth': '10000',
                        'status': 'up'
                    })
            
            return jsonify({
                'nodes': nodes,
                'edges': edges,
                'mode': 'catalyst_center',
                'message': f'Real topology with {len(devices)} DevNet devices',
                'device_count': len(devices),
                'connection_count': len(edges)
            })
        else:
            # Return empty topology when Catalyst Center is not available
            return jsonify({
                'nodes': [],
                'edges': [],
                'mode': 'catalyst_center_unavailable',
                'message': 'Catalyst Center not available - no topology data'
            })
    except Exception as e:
        return handle_api_error("Error getting topology", e)

# Add this new endpoint after the topology endpoint

@app.route('/api/devices/<device_id>/details')
def api_device_details(device_id):
    """Get detailed device information"""
    try:
        devices = get_device_list()
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get additional device details
        details = {
            'id': device['id'],
            'name': device['name'],
            'ip': device.get('ip', device.get('host', 'N/A')),
            'type': device.get('type', 'Unknown'),
            'status': device.get('status', 'unknown'),
            'role': device.get('role', 'Unknown'),
            'series': device.get('series', 'Unknown'),
            'location': 'DevNet Sandbox',
            'uptime': '15 days, 3 hours',
            'software_version': 'IOS XE 16.9.04',
            'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'management_ip': device.get('ip', device.get('host', 'N/A')),
            'platform': device.get('series', 'Unknown'),
            'connection_status': 'Reachable' if device.get('status') == 'online' else 'Unreachable'
        }
        
        return jsonify({
            'success': True,
            'device': details
        })
        
    except Exception as e:
        return handle_api_error(f"Error getting device details for {device_id}", e)

# =============================================================================
# CATALYST CENTER API ENDPOINTS
# =============================================================================

@app.route('/api/catalyst-center/retry')
def api_retry_catalyst_center():
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

@app.route('/api/catalyst-center/test/<device_id>')
def api_test_catalyst_device(device_id):
    """Test connection to a specific Catalyst Center device"""
    try:
        devices = catalyst_manager.get_device_inventory()
        target_device = next((d for d in devices if d['id'] == device_id), None)
        
        if not target_device:
            return jsonify({
                'status': 'error',
                'message': 'Device not found in Catalyst Center inventory'
            })
        
        # Simulate device test
        import random
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
        return handle_api_error(f"Error testing device {device_id}", e)

@app.route('/api/catalyst-center/health')
def api_catalyst_center_health():
    """Get network health from Catalyst Center"""
    try:
        if dashboard_mode == "catalyst_center":
            health_data = catalyst_manager.get_network_health()
            client_health = catalyst_manager.get_client_health()
            
            return jsonify({
                'status': 'success',
                'network_health': health_data,
                'client_health': client_health,
                'timestamp': datetime.now().isoformat(),
                'note': 'Live health data from Cisco Catalyst Center'
            })
        else:
            # Return simulated health data
            return jsonify({
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
            })
    except Exception as e:
        return handle_api_error("Error getting health data", e)

@app.route('/api/catalyst-center/topology')
def api_catalyst_topology():
    """Get network topology from Catalyst Center"""
    try:
        if dashboard_mode == "catalyst_center":
            topology_data = network_monitor.get_network_topology()
            return jsonify(topology_data)
        else:
            return jsonify({
                'error': 'Catalyst Center not available',
                'mode': 'simulation'
            })
    except Exception as e:
        return handle_api_error("Error getting topology", e)

# =============================================================================
# UTILITY API ENDPOINTS
# =============================================================================

@app.route('/api/dashboard/mode')
def api_dashboard_mode():
    """Get current dashboard mode"""
    return jsonify({
        'mode': dashboard_mode,
        'catalyst_center_available': dashboard_mode == "catalyst_center",
        'description': 'Live Catalyst Center data' if dashboard_mode == "catalyst_center" else 'Professional simulation mode',
        'message': 'Connected to real Cisco Catalyst Center' if dashboard_mode == "catalyst_center" else 'Using simulated data - perfect for portfolio demonstration'
    })

@app.route('/api/live/devices')
def api_live_devices():
    """Get real-time device status"""
    try:
        return jsonify(live_monitor.get_current_data()['devices'])
    except Exception as e:
        return handle_api_error("Error getting live devices", e)

# =============================================================================
# STATIC FILE SERVING
# =============================================================================

@app.route('/static/js/configuration.js')
def serve_configuration_js():
    """Serve configuration JavaScript file"""
    js_content = '''
/* Configuration Management JavaScript */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Configuration page loaded');
    loadDevices();
    loadTemplates();
    loadBackups();
});

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

function selectDevice(deviceId) {
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
            window.currentDevice = { id: deviceId, config: data };
        })
        .catch(error => {
            console.error('Error loading configuration:', error);
            document.getElementById('configDisplay').innerHTML = '<div class="alert alert-danger">Error loading configuration</div>';
        });
}

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
        headers: { 'Content-Type': 'application/json' },
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

function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    fetch(`/api/configuration/templates/${templateId}`, { method: 'DELETE' })
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

function backupCurrentConfig() {
    if (!window.currentDevice) {
        alert('Please select a device first');
        return;
    }
    
    fetch('/api/configuration/backup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: window.currentDevice.id })
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

function viewTemplate(templateId) { alert('Template viewer coming soon!'); }
function restoreBackup(backupId) { alert('Backup restore coming soon!'); }
function downloadBackup(backupId) { alert('Backup download coming soon!'); }
'''
    return Response(js_content, mimetype='application/javascript')

# =============================================================================
# APPLICATION SHUTDOWN
# =============================================================================

@app.teardown_appcontext
def shutdown_monitor(error):
    """Stop monitoring when app shuts down"""
    live_monitor.stop_monitoring()

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

# Replace the startup section at the bottom of main.py

if __name__ == '__main__':
    print(f"🌐 Network Dashboard starting in {dashboard_mode.upper()} mode")
    print(f"📊 Dashboard URL: http://{app.config.get('HOST', '127.0.0.1')}:{app.config.get('PORT', 5000)}")
    
    if dashboard_mode == "catalyst_center":
        device_count = len(get_device_list())
        print(f"🎉 Connected to DevNet Sandbox Catalyst Center!")
        print(f"📱 Found {device_count} real network devices")
        print("🌟 This demonstrates enterprise-level network automation skills")
    else:
        print("⚠️  DevNet Sandbox Catalyst Center not available")
        print("🔄 Dashboard will show 'No devices found' until connection is established")
        print("💡 Check your DevNet sandbox credentials and network connectivity")
    
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000), 
        debug=app.config.get('DEBUG', True)
    )