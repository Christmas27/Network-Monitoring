#!/usr/bin/env python3
"""
Reusable Form Components for Network Monitoring Dashboard
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

def add_device_form(device_manager, on_success: Optional[Callable] = None):
    """
    Reusable add device form component
    
    Args:
        device_manager: DeviceManager instance
        on_success: Callback function to run on successful device addition
    """
    with st.form("add_device_form"):
        st.subheader("➕ Add New Device")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hostname = st.text_input(
                "🏷️ Hostname", 
                placeholder="lab-router1",
                help="Unique device hostname"
            )
            ip_address = st.text_input(
                "🌐 IP Address", 
                placeholder="127.0.0.1:2221",
                help="IP address and port for SSH connection"
            )
            device_type = st.selectbox(
                "📱 Device Type", 
                ["router", "switch", "firewall", "server", "access_point"],
                help="Select the device type"
            )
        
        with col2:
            manufacturer = st.text_input(
                "🏭 Manufacturer", 
                placeholder="Cisco",
                help="Device manufacturer"
            )
            model = st.text_input(
                "📦 Model", 
                placeholder="ISR4331",
                help="Device model number"
            )
            tags = st.text_input(
                "🏷️ Tags", 
                placeholder="lab,production,core",
                help="Comma-separated tags for grouping"
            )
        
        # Credentials section
        st.markdown("### 🔐 SSH Credentials")
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "👤 Username", 
                value="admin",
                help="SSH username"
            )
        
        with col2:
            password = st.text_input(
                "🔒 Password", 
                value="admin",
                type="password",
                help="SSH password"
            )
        
        # Additional settings
        with st.expander("⚙️ Advanced Settings"):
            ssh_port = st.number_input("SSH Port", value=22, min_value=1, max_value=65535)
            connection_timeout = st.number_input("Connection Timeout (s)", value=10, min_value=1, max_value=60)
            enable_monitoring = st.checkbox("Enable Monitoring", value=True)
            enable_security_scan = st.checkbox("Enable Security Scanning", value=True)
        
        submitted = st.form_submit_button("➕ Add Device", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not hostname:
                st.error("❌ Hostname is required")
                return False
            
            if not ip_address:
                st.error("❌ IP Address is required")
                return False
            
            # Prepare device data
            device_data = {
                'hostname': hostname,
                'ip_address': ip_address,
                'device_type': device_type,
                'manufacturer': manufacturer,
                'model': model,
                'tags': tags,
                'username': username,
                'password': password,
                'ssh_port': ssh_port,
                'timeout': connection_timeout,
                'monitoring_enabled': enable_monitoring,
                'security_scan_enabled': enable_security_scan,
                'status': 'unknown',
                'created_at': datetime.now().isoformat()
            }
            
            try:
                result = device_manager.add_device(**device_data)
                if result:
                    st.success(f"✅ Device '{hostname}' added successfully!")
                    if on_success:
                        on_success()
                    return True
                else:
                    st.error("❌ Failed to add device")
                    return False
            except Exception as e:
                st.error(f"❌ Error adding device: {str(e)}")
                return False

def device_selector(devices: List[Dict[str, Any]], key: str = "device_selector") -> Optional[Dict[str, Any]]:
    """
    Reusable device selector component
    
    Args:
        devices: List of device dictionaries
        key: Unique key for the selector
        
    Returns:
        Selected device dictionary or None
    """
    if not devices:
        st.warning("⚠️ No devices available")
        return None
    
    device_options = ["Select a device..."] + [
        f"{d['hostname']} ({d['ip_address']}) - {d.get('status', 'unknown').upper()}" 
        for d in devices
    ]
    
    selected_option = st.selectbox(
        "🎯 Choose device:",
        device_options,
        key=key
    )
    
    if selected_option == "Select a device...":
        return None
    
    # Find the selected device
    for device in devices:
        if f"{device['hostname']} ({device['ip_address']}) - {device.get('status', 'unknown').upper()}" == selected_option:
            return device
    
    return None

def lab_device_selector(devices: List[Dict[str, Any]], key: str = "lab_device_selector") -> Optional[Dict[str, Any]]:
    """
    Reusable lab device selector component (filters for lab devices only)
    
    Args:
        devices: List of device dictionaries
        key: Unique key for the selector
        
    Returns:
        Selected lab device dictionary or None
    """
    # Filter for lab devices
    lab_devices = []
    for d in devices:
        has_lab_tag = 'lab' in d.get('tags', '')
        uses_lab_port = any(port in str(d.get('ip_address', '')) for port in ['2221', '2222', '2223'])
        if has_lab_tag or uses_lab_port:
            lab_devices.append(d)
    
    if not lab_devices:
        st.warning("⚠️ No lab devices available. Add lab devices first.")
        return None
    
    return device_selector(lab_devices, key)

def playbook_selector(playbooks: List[Dict[str, Any]], key: str = "playbook_selector") -> Optional[Dict[str, Any]]:
    """
    Reusable playbook selector component
    
    Args:
        playbooks: List of playbook dictionaries
        key: Unique key for the selector
        
    Returns:
        Selected playbook dictionary or None
    """
    if not playbooks:
        st.warning("⚠️ No playbooks available")
        return None
    
    playbook_names = [pb.get('name', pb.get('filename', 'Unknown')) for pb in playbooks]
    
    selected_name = st.selectbox(
        "📄 Select Playbook:",
        ["Select a playbook..."] + playbook_names,
        key=key
    )
    
    if selected_name == "Select a playbook...":
        return None
    
    # Find the selected playbook
    for playbook in playbooks:
        if playbook.get('name', playbook.get('filename', 'Unknown')) == selected_name:
            return playbook
    
    return None

def ssh_operation_selector(key: str = "ssh_operation_selector") -> str:
    """
    Reusable SSH operation selector component
    
    Args:
        key: Unique key for the selector
        
    Returns:
        Selected operation string
    """
    operations = [
        "🔗 SSH Connectivity Test",
        "⚙️ Configuration Deployment", 
        "📊 System Monitoring",
        "🧪 Custom Command Execution",
        "💾 Configuration Backup",
        "🛡️ Security Assessment"
    ]
    
    return st.selectbox("📄 Select Operation", operations, key=key)

def security_scan_controls(devices: List[Dict[str, Any]], key_prefix: str = "security") -> Dict[str, Any]:
    """
    Reusable security scanning controls
    
    Args:
        devices: List of devices
        key_prefix: Prefix for form keys
        
    Returns:
        Dictionary with scan parameters and selected device
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # Device selection
        selected_device = device_selector(devices, f"{key_prefix}_device_selector")
        
        # Scan controls
        col_a, col_b = st.columns(2)
        with col_a:
            port_scan_btn = st.button("🔍 Port Scan", use_container_width=True, key=f"{key_prefix}_port_scan")
        with col_b:
            ssh_scan_btn = st.button("🔐 SSH Analysis", use_container_width=True, key=f"{key_prefix}_ssh_scan")
        
        comprehensive_scan_btn = st.button(
            "🚨 Full Security Scan", 
            use_container_width=True, 
            type="primary",
            key=f"{key_prefix}_full_scan"
        )
    
    with col2:
        # Scan options
        st.markdown("#### 🔧 Scan Options")
        
        port_range = st.text_input(
            "Port Range", 
            value="22,80,443,8080", 
            help="Comma-separated ports or ranges (e.g., 22,80-90,443)",
            key=f"{key_prefix}_port_range"
        )
        
        timeout = st.slider(
            "Timeout (seconds)", 
            min_value=1, 
            max_value=30, 
            value=5,
            key=f"{key_prefix}_timeout"
        )
        
        aggressive_scan = st.checkbox(
            "Aggressive Scan", 
            value=False,
            help="More thorough but slower scanning",
            key=f"{key_prefix}_aggressive"
        )
    
    return {
        'selected_device': selected_device,
        'port_scan_btn': port_scan_btn,
        'ssh_scan_btn': ssh_scan_btn,
        'comprehensive_scan_btn': comprehensive_scan_btn,
        'port_range': port_range,
        'timeout': timeout,
        'aggressive_scan': aggressive_scan
    }

def configuration_template_form(config_manager, key_prefix: str = "config") -> Dict[str, Any]:
    """
    Reusable configuration template form
    
    Args:
        config_manager: ConfigManager instance
        key_prefix: Prefix for form keys
        
    Returns:
        Dictionary with template data
    """
    with st.form(f"{key_prefix}_template_form"):
        st.subheader("📄 Create Configuration Template")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input(
                "Template Name", 
                placeholder="Basic Router Config",
                key=f"{key_prefix}_template_name"
            )
            device_type = st.selectbox(
                "Device Type", 
                ["router", "switch", "firewall", "server"],
                key=f"{key_prefix}_device_type"
            )
        
        with col2:
            description = st.text_area(
                "Description", 
                placeholder="Basic configuration template for lab routers",
                key=f"{key_prefix}_description"
            )
        
        # Template content
        template_content = st.text_area(
            "Template Content (Jinja2)", 
            placeholder="""hostname {{ hostname }}
!
interface GigabitEthernet0/0
 ip address {{ mgmt_ip }} {{ mgmt_mask }}
 no shutdown
!
""",
            height=200,
            key=f"{key_prefix}_content"
        )
        
        # Variables section
        st.markdown("#### 📋 Template Variables")
        variables = st.text_area(
            "Variables (JSON format)", 
            placeholder='{"mgmt_ip": "192.168.1.1", "mgmt_mask": "255.255.255.0"}',
            key=f"{key_prefix}_variables"
        )
        
        submitted = st.form_submit_button("💾 Save Template", type="primary")
        
        if submitted:
            return {
                'template_name': template_name,
                'device_type': device_type,
                'description': description,
                'template_content': template_content,
                'variables': variables,
                'submitted': True
            }
        
        return {'submitted': False}
