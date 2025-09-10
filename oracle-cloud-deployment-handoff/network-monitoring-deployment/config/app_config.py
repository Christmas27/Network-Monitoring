#!/usr/bin/env python3
"""
Application Configuration for Network Monitoring Dashboard
"""

import streamlit as st
from datetime import datetime

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Network Monitoring Dashboard",
    "page_icon": "🌐",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://github.com/Christmas27/Network-Monitoring',
        'Report a bug': 'https://github.com/Christmas27/Network-Monitoring/issues',
        'About': "Network Monitoring Dashboard - 100% Python Implementation"
    }
}

# Application Pages
PAGES = [
    "🏠 Dashboard", 
    "📱 Devices", 
    "🤖 Automation", 
    "🛡️ Security", 
    "⚙️ Configuration", 
    "🔍 Monitoring", 
    "🌐 Topology"
]

# Device Types and Icons
DEVICE_TYPES = {
    'router': {
        'emoji': '🔀',
        'name': 'Router',
        'color': '#28a745'
    },
    'switch': {
        'emoji': '🔗',
        'name': 'Switch',
        'color': '#007bff'
    },
    'firewall': {
        'emoji': '🛡️',
        'name': 'Firewall',
        'color': '#dc3545'
    },
    'server': {
        'emoji': '🖥️',
        'name': 'Server',
        'color': '#6f42c1'
    },
    'access_point': {
        'emoji': '📡',
        'name': 'Access Point',
        'color': '#fd7e14'
    }
}

# Status Types and Colors
STATUS_TYPES = {
    'online': {
        'emoji': '🟢',
        'color': '#28a745',
        'text': 'Online'
    },
    'offline': {
        'emoji': '🔴',
        'color': '#dc3545',
        'text': 'Offline'
    },
    'unknown': {
        'emoji': '⚪',
        'color': '#6c757d',
        'text': 'Unknown'
    },
    'maintenance': {
        'emoji': '🟡',
        'color': '#ffc107',
        'text': 'Maintenance'
    }
}

# Security Severity Levels
SECURITY_SEVERITY = {
    'critical': {
        'emoji': '🔴',
        'color': '#dc3545',
        'priority': 1
    },
    'high': {
        'emoji': '🟠',
        'color': '#fd7e14',
        'priority': 2
    },
    'medium': {
        'emoji': '🟡',
        'color': '#ffc107',
        'priority': 3
    },
    'low': {
        'emoji': '🟢',
        'color': '#20c997',
        'priority': 4
    },
    'info': {
        'emoji': '🔵',
        'color': '#17a2b8',
        'priority': 5
    }
}

# Default Lab Configuration
DEFAULT_LAB_DEVICES = [
    {
        'hostname': 'lab-router1',
        'ip_address': '127.0.0.1:2221',
        'device_type': 'router',
        'manufacturer': 'LinuxServer',
        'model': 'OpenSSH Container',
        'tags': 'lab,router,testing',
        'username': 'admin',
        'password': 'admin',
        'ssh_port': 2221
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
        'ssh_port': 2222
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
        'ssh_port': 2223
    }
]

# SSH Operations
SSH_OPERATIONS = [
    "🔗 SSH Connectivity Test",
    "⚙️ Configuration Deployment", 
    "📊 System Monitoring",
    "🧪 Custom Command Execution",
    "💾 Configuration Backup",
    "🛡️ Security Assessment"
]

# Configuration Template Types
TEMPLATE_TYPES = {
    'router': [
        'Basic Router Configuration',
        'OSPF Configuration',
        'BGP Configuration',
        'Security Hardening'
    ],
    'switch': [
        'Basic Switch Configuration',
        'VLAN Configuration',
        'Port Security',
        'QoS Configuration'
    ],
    'firewall': [
        'Basic Firewall Rules',
        'VPN Configuration',
        'IDS/IPS Rules',
        'DMZ Configuration'
    ]
}

# Monitoring Thresholds
MONITORING_THRESHOLDS = {
    'cpu_usage': {
        'normal': 70,
        'warning': 85,
        'critical': 95
    },
    'memory_usage': {
        'normal': 80,
        'warning': 90,
        'critical': 95
    },
    'response_time': {
        'excellent': 100,
        'good': 500,
        'poor': 1000
    }
}

# Chart Colors (Nordic Theme)
CHART_COLORS = {
    'primary': '#5e81ac',
    'success': '#a3be8c',
    'warning': '#ebcb8b',
    'error': '#bf616a',
    'info': '#81a1c1',
    'secondary': '#4c566a'
}

def apply_page_config():
    """Apply Streamlit page configuration"""
    st.set_page_config(**PAGE_CONFIG)

def get_device_emoji(device_type: str) -> str:
    """Get emoji for device type"""
    return DEVICE_TYPES.get(device_type, {}).get('emoji', '📱')

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    return STATUS_TYPES.get(status, {}).get('emoji', '⚪')

def get_severity_emoji(severity: str) -> str:
    """Get emoji for security severity"""
    return SECURITY_SEVERITY.get(severity, {}).get('emoji', '⚪')

def format_timestamp(timestamp=None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_app_footer() -> str:
    """Get application footer HTML"""
    return f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🐍 <strong>100% Python Network Monitoring Dashboard</strong></p>
        <p>Powered by Streamlit • No JavaScript Required • {format_timestamp()}</p>
    </div>
    """

# Session State Keys
SESSION_KEYS = {
    'device_manager': 'device_manager',
    'network_monitor': 'network_monitor',
    'security_scanner': 'security_scanner',
    'config_manager': 'config_manager',
    'ansible_manager': 'ansible_manager',
    'ssh_manager': 'ssh_manager',
    'real_ssh_manager': 'real_ssh_manager',
    'topology_manager': 'topology_manager',
    'wsl_ansible_bridge': 'wsl_ansible_bridge',
    'catalyst_manager': 'catalyst_manager',
    'automation_history': 'automation_history',
    'last_refresh': 'last_refresh',
    'cached_playbooks': 'cached_playbooks'
}
