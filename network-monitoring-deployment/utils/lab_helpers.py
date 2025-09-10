#!/usr/bin/env python3
"""
Lab Helper Utilities for Network Monitoring Dashboard
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_lab_devices(device_manager) -> List[Dict[str, Any]]:
    """
    Get all lab devices from the device manager
    
    Args:
        device_manager: DeviceManager instance
        
    Returns:
        List of lab device dictionaries
    """
    try:
        all_devices = device_manager.get_all_devices()
        lab_devices = []
        
        for device in all_devices:
            # Check if device has 'lab' tag OR uses lab ports (2221, 2222, 2223)
            has_lab_tag = 'lab' in device.get('tags', '')
            uses_lab_port = any(port in str(device.get('ip_address', '')) for port in ['2221', '2222', '2223'])
            
            if has_lab_tag or uses_lab_port:
                lab_devices.append(device)
        
        return lab_devices
        
    except Exception as e:
        logger.error(f"Error getting lab devices: {e}")
        return []

def ensure_default_lab_devices(device_manager) -> List[Dict[str, Any]]:
    """
    Ensure default lab devices exist in the database
    
    Args:
        device_manager: DeviceManager instance
        
    Returns:
        List of lab devices (existing + newly created)
    """
    try:
        # Check if lab devices already exist
        existing_lab_devices = get_lab_devices(device_manager)
        
        if existing_lab_devices:
            return existing_lab_devices
        
        # Create default lab devices
        default_devices = [
            {
                'hostname': 'lab-router1',
                'ip_address': '127.0.0.1:2221',
                'device_type': 'router',
                'manufacturer': 'LinuxServer',
                'model': 'OpenSSH Container',
                'tags': 'lab,router,testing',
                'username': 'admin',
                'password': 'admin',
                'ssh_port': 2221,
                'status': 'unknown'
            },
            {
                'hostname': 'lab-switch1',
                'ip_address': '127.0.0.1:2222',
                'device_type': 'switch',
                'manufacturer': 'LinuxServer',
                'model': 'OpenSSH Container',
                'tags': 'lab,switch,testing',
                'username': 'admin',
                'password': 'admin',
                'ssh_port': 2222,
                'status': 'unknown'
            },
            {
                'hostname': 'lab-firewall1',
                'ip_address': '127.0.0.1:2223',
                'device_type': 'firewall',
                'manufacturer': 'LinuxServer',
                'model': 'OpenSSH Container',
                'tags': 'lab,firewall,testing',
                'username': 'admin',
                'password': 'admin',
                'ssh_port': 2223,
                'status': 'unknown'
            }
        ]
        
        created_devices = []
        for device_data in default_devices:
            try:
                result = device_manager.add_device(**device_data)
                if result:
                    created_devices.append(device_data)
                    logger.info(f"Created default lab device: {device_data['hostname']}")
            except Exception as e:
                logger.warning(f"Failed to create lab device {device_data['hostname']}: {e}")
        
        return get_lab_devices(device_manager)  # Return updated list
        
    except Exception as e:
        logger.error(f"Error ensuring default lab devices: {e}")
        return []

def is_lab_device(device: Dict[str, Any]) -> bool:
    """
    Check if a device is a lab device
    
    Args:
        device: Device dictionary
        
    Returns:
        True if device is a lab device
    """
    # Check if device has 'lab' tag
    if 'lab' in device.get('tags', ''):
        return True
    
    # Check if device uses lab ports
    ip_address = str(device.get('ip_address', ''))
    lab_ports = ['2221', '2222', '2223']
    
    return any(port in ip_address for port in lab_ports)

def get_lab_device_status(device_manager, ssh_manager) -> Dict[str, str]:
    """
    Get status of all lab devices
    
    Args:
        device_manager: DeviceManager instance
        ssh_manager: SSH manager instance
        
    Returns:
        Dictionary mapping device hostnames to status
    """
    lab_devices = get_lab_devices(device_manager)
    status_map = {}
    
    for device in lab_devices:
        try:
            # Test SSH connectivity
            hostname = device.get('hostname', 'unknown')
            ip_parts = device.get('ip_address', '').split(':')
            
            if len(ip_parts) == 2:
                host = ip_parts[0]
                port = int(ip_parts[1])
                
                # Use SSH manager to test connection
                result = ssh_manager.test_connection(host, port, 
                                                   device.get('username', 'admin'),
                                                   device.get('password', 'admin'))
                
                status_map[hostname] = 'online' if result.get('success') else 'offline'
            else:
                status_map[hostname] = 'unknown'
                
        except Exception as e:
            logger.error(f"Error testing device {device.get('hostname')}: {e}")
            status_map[hostname] = 'error'
    
    return status_map

def format_device_display_name(device: Dict[str, Any]) -> str:
    """
    Format device for display in selectboxes
    
    Args:
        device: Device dictionary
        
    Returns:
        Formatted display string
    """
    hostname = device.get('hostname', 'Unknown')
    ip_address = device.get('ip_address', 'N/A')
    status = device.get('status', 'unknown').upper()
    
    # Add emoji based on device type
    type_emoji = {
        'router': '🔀',
        'switch': '🔗',
        'firewall': '🛡️',
        'server': '🖥️',
        'access_point': '📡'
    }.get(device.get('device_type', 'unknown'), '📱')
    
    return f"{type_emoji} {hostname} ({ip_address}) - {status}"

def get_device_type_stats(devices: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get statistics about device types
    
    Args:
        devices: List of device dictionaries
        
    Returns:
        Dictionary with device type counts
    """
    stats = {}
    
    for device in devices:
        device_type = device.get('device_type', 'unknown')
        stats[device_type] = stats.get(device_type, 0) + 1
    
    return stats

def validate_lab_environment() -> Dict[str, Any]:
    """
    Validate that lab environment is properly set up
    
    Returns:
        Dictionary with validation results
    """
    import docker
    
    validation_results = {
        'docker_available': False,
        'lab_containers_running': False,
        'container_count': 0,
        'containers': [],
        'recommendations': []
    }
    
    try:
        # Check Docker availability
        client = docker.from_env()
        validation_results['docker_available'] = True
        
        # Check for lab containers
        lab_containers = client.containers.list(filters={'name': 'lab-'})
        validation_results['container_count'] = len(lab_containers)
        
        running_containers = []
        for container in lab_containers:
            container_info = {
                'name': container.name,
                'status': container.status,
                'ports': container.ports
            }
            running_containers.append(container_info)
            
        validation_results['containers'] = running_containers
        validation_results['lab_containers_running'] = len(running_containers) > 0
        
        # Generate recommendations
        if not validation_results['lab_containers_running']:
            validation_results['recommendations'].append(
                "Start lab containers using: docker-compose up -d"
            )
        
        if validation_results['container_count'] < 3:
            validation_results['recommendations'].append(
                "Consider adding more lab devices for comprehensive testing"
            )
            
    except Exception as e:
        logger.error(f"Error validating lab environment: {e}")
        validation_results['recommendations'].append(
            "Docker is not available or not running"
        )
    
    return validation_results

def get_lab_connection_info() -> Dict[str, Dict[str, Any]]:
    """
    Get connection information for lab devices
    
    Returns:
        Dictionary with connection details for each lab device
    """
    return {
        'lab-router1': {
            'host': '127.0.0.1',
            'port': 2221,
            'username': 'admin',
            'password': 'admin',
            'device_type': 'router',
            'description': 'Lab Router 1 - Core routing device'
        },
        'lab-switch1': {
            'host': '127.0.0.1',
            'port': 2222,
            'username': 'admin',
            'password': 'admin',
            'device_type': 'switch',
            'description': 'Lab Switch 1 - Access layer device'
        },
        'lab-firewall1': {
            'host': '127.0.0.1',
            'port': 2223,
            'username': 'admin',
            'password': 'admin',
            'device_type': 'firewall',
            'description': 'Lab Firewall 1 - Security device'
        }
    }
